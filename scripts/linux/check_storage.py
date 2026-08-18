#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IndieTracks 本地存储检测与专辑清理脚本。

由 run-crawlers.sh 在运行爬虫前调用（也可单独运行）：
1. 报告 IndieTracks 项目占用总大小、PostgreSQL 数据库大小、MinIO 存储卷大小；
2. 询问是否需要删除专辑文件以压缩空间；
3. 按专辑发布时间从旧到新生成删除清单，直到累计大小达到用户输入的目标；
4. 用户确认后删除清单内专辑的 MinIO 文件与数据库专辑记录。
"""

import json
import os
import re
import sys

import psycopg2
from minio import Minio

GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
NC = "\033[0m"


def info(msg):
    print(f"{GREEN}[INFO]{NC} {msg}")


def warn(msg):
    print(f"{YELLOW}[WARN]{NC} {msg}")


def error(msg):
    print(f"{RED}[ERROR]{NC} {msg}", file=sys.stderr)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def human_size(num):
    """把字节数转成人类可读格式（二进制单位）。"""
    num = float(num)
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    for unit in units:
        if num < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(num)} B"
            return f"{num:.2f} {unit}"
        num /= 1024.0
    return f"{num:.2f} PiB"


def parse_size(text):
    """解析用户输入的容量，如 1.2GB / 500MB / 800MiB / 1024。无单位时按 GB 理解。"""
    s = text.strip().lower()
    m = re.match(r"^(\d+(?:\.\d+)?)\s*([kmgt]?i?b?)$", s)
    if not m:
        return None
    number = float(m.group(1))
    unit = m.group(2)
    table = {
        "": 1024 ** 3,  # 未输入单位，按 GB
        "b": 1,
        "k": 1024, "kb": 1024, "ki": 1024, "kib": 1024,
        "m": 1024 ** 2, "mb": 1024 ** 2, "mi": 1024 ** 2, "mib": 1024 ** 2,
        "g": 1024 ** 3, "gb": 1024 ** 3, "gi": 1024 ** 3, "gib": 1024 ** 3,
        "t": 1024 ** 4, "tb": 1024 ** 4, "ti": 1024 ** 4, "tib": 1024 ** 4,
    }
    return int(number * table[unit])


def prompt_yes_no(prompt):
    """询问 y/N，返回布尔值。"""
    try:
        ans = input(prompt).strip().lower()
    except EOFError:
        return False
    return ans in ("y", "yes")


def fmt_publish_date(pub):
    if pub is None:
        return "未知"
    if hasattr(pub, "strftime"):
        return pub.strftime("%Y-%m-%d")
    return str(pub)[:10]


def main():
    db_config = os.environ.get("DB_CONFIG")
    minio_config = os.environ.get("MINIO_CONFIG")
    if not db_config or not minio_config:
        error("缺少环境变量 DB_CONFIG / MINIO_CONFIG")
        return 1

    db_cfg = load_json(db_config)
    minio_cfg = load_json(minio_config)

    db_host = db_cfg.get("host", "localhost")
    db_port = int(db_cfg.get("port", 5432))
    db_name = db_cfg.get("database", "indietracks")
    db_user = db_cfg.get("user", "postgres")
    db_pass = db_cfg.get("password", "postgres")

    endpoint = minio_cfg.get("endpoint", "http://localhost:9000")
    access_key = minio_cfg.get("access_key", "minioadmin")
    secret_key = minio_cfg.get("secret_key", "minioadmin")
    bucket = minio_cfg.get("bucket", "indietracks")
    prefixes = minio_cfg.get("prefixes", {})
    cover_prefix = prefixes.get("covers", "covers/")
    audio_prefixes = [
        prefixes.get("audio_preview", "audio/preview/"),
        prefixes.get("audio_full", "audio/full/"),
    ]

    print("=" * 56)
    print("  IndieTracks 本地存储检测")
    print("=" * 56)
    print()

    # ── 连接 PostgreSQL ─────────────────────────
    try:
        conn = psycopg2.connect(
            host=db_host, port=db_port, dbname=db_name,
            user=db_user, password=db_pass,
        )
    except Exception as exc:
        error(f"无法连接 PostgreSQL：{exc}")
        return 1
    cur = conn.cursor()

    # ── 连接 MinIO ──────────────────────────────
    endpoint_host = endpoint.replace("https://", "").replace("http://", "").rstrip("/")
    secure = endpoint.startswith("https://")
    try:
        client = Minio(
            endpoint_host,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        if not client.bucket_exists(bucket):
            error(f"MinIO bucket 不存在：{bucket}")
            conn.close()
            return 1
    except Exception as exc:
        error(f"无法连接 MinIO：{exc}")
        conn.close()
        return 1

    # ── 计算并报告存储占用 ─────────────────────
    try:
        cur.execute("SELECT pg_database_size(%s)", (db_name,))
        db_size = int(cur.fetchone()[0])
    except Exception as exc:
        error(f"查询 PostgreSQL 数据库大小失败：{exc}")
        conn.close()
        return 1

    minio_total = 0
    minio_objects = 0
    try:
        for obj in client.list_objects(bucket, recursive=True):
            minio_total += obj.size
            minio_objects += 1
    except Exception as exc:
        error(f"统计 MinIO 存储卷大小失败：{exc}")
        conn.close()
        return 1

    total_size = db_size + minio_total

    print("  项目存储占用总大小：", human_size(total_size))
    print("    ├─ PostgreSQL 数据库：", human_size(db_size))
    print("    └─ MinIO 存储卷：", human_size(minio_total), f"（{minio_objects} 个对象）")
    print()

    # ── 询问是否清理专辑文件 ───────────────────
    if not prompt_yes_no("  是否需要删除专辑文件以压缩空间？[y/N] "):
        print()
        info("已选择不清理，继续爬虫流程。")
        conn.close()
        return 0

    print()
    target = None
    while target is None or target <= 0:
        try:
            raw = input("  请输入需要删除的专辑文件大小（例如：1.2GB，无单位默认 GB）：").strip()
        except EOFError:
            print()
            conn.close()
            return 0
        target = parse_size(raw)
        if target is None or target <= 0:
            warn(f"无法识别容量：{raw!r}，请重新输入（如 1.2GB / 500MB）")
            target = None
    print()
    info(f"目标删除大小：{human_size(target)}")
    print()

    # ── 生成删除清单（发布时间从旧到新） ───────
    cur.execute(
        """
        SELECT album_id, dizzylab_id, title, cover_url, publish_date
        FROM albums
        ORDER BY publish_date ASC NULLS LAST, album_id ASC
        """
    )
    albums = cur.fetchall()

    plan = []
    skipped_empty = 0
    cumulative = 0
    reached = False

    for aid, slug, title, cover, pub in albums:
        keys = []  # (object_key, db_file_size)

        # 专辑封面
        if cover and cover.startswith(cover_prefix):
            keys.append((cover, 0))

        # 专辑音频
        cur.execute(
            "SELECT object_key, file_size FROM work_files WHERE album_id = %s ORDER BY sort_order",
            (aid,),
        )
        for obj_key, file_size in cur.fetchall():
            if not obj_key:
                continue
            if any(obj_key.startswith(p) for p in audio_prefixes):
                keys.append((obj_key, int(file_size or 0)))

        # 去重后向 MinIO 查询实际大小
        unique_keys = {}
        for key, fallback in keys:
            unique_keys[key] = fallback

        album_size = 0
        key_sizes = {}
        for key, fallback in unique_keys.items():
            size = fallback
            try:
                st = client.stat_object(bucket, key)
                size = st.size
            except Exception:
                # 对象不存在或查询失败时，回退到数据库记录的 file_size
                pass
            key_sizes[key] = size
            album_size += size

        if album_size <= 0:
            skipped_empty += 1
            continue

        plan.append({
            "album_id": aid,
            "title": title,
            "publish_date": pub,
            "total": album_size,
            "keys": key_sizes,
        })
        cumulative += album_size
        if cumulative >= target:
            reached = True
            break

    if not plan:
        print()
        warn("未找到任何包含 MinIO 文件的专辑，无需删除。")
        conn.close()
        return 0

    # ── 打印删除清单 ───────────────────────────
    print()
    print("  按发布时间从旧到新，累计达到目标大小的专辑删除清单：")
    print("  " + "-" * 104)
    print(f"  {'序号':<4} {'专辑ID':<8} {'发布时间':<12} {'专辑大小':<14} {'累计大小':<14} 标题")
    print("  " + "-" * 104)

    shown_cumulative = 0
    for idx, item in enumerate(plan, 1):
        shown_cumulative += item["total"]
        pub_s = fmt_publish_date(item["publish_date"])
        title_s = item["title"] if item["title"] else "(无标题)"
        if len(title_s) > 40:
            title_s = title_s[:39] + "…"
        print(
            f"  {idx:<4} {item['album_id']:<8} {pub_s:<12} "
            f"{human_size(item['total']):<14} {human_size(shown_cumulative):<14} {title_s}"
        )

    print("  " + "-" * 104)
    if not reached:
        warn(f"所有可删除专辑文件合计仅 {human_size(shown_cumulative)}，未达到目标 {human_size(target)}。")
    info(f"清单共 {len(plan)} 张专辑，累计专辑文件大小：{human_size(shown_cumulative)}")
    if skipped_empty:
        print(f"  （另有 {skipped_empty} 张专辑没有 MinIO 文件，已跳过）")

    # ── 二次确认 ───────────────────────────────
    print()
    if not prompt_yes_no(f"  是否确认删除以上 {len(plan)} 张专辑？[y/N] "):
        print()
        info("已取消删除，未做任何更改。")
        conn.close()
        return 0

    # ── 删除 MinIO 文件 ────────────────────────
    print()
    freed = 0
    failed_keys = []
    for idx, item in enumerate(plan, 1):
        aid = item["album_id"]
        title_s = item["title"] if item["title"] else "(无标题)"
        print(f"  [{idx}/{len(plan)}] 删除专辑 {aid}（{title_s}）的 MinIO 文件 ...")
        for key, size in item["keys"].items():
            try:
                client.remove_object(bucket, key)
                freed += size
            except Exception as exc:
                failed_keys.append((key, str(exc)))

    if failed_keys:
        print()
        warn(f"有 {len(failed_keys)} 个 MinIO 对象删除失败：")
        for key, msg in failed_keys[:20]:
            print(f"    - {key}: {msg}")
        if len(failed_keys) > 20:
            print(f"    ... 其余 {len(failed_keys) - 20} 个略")
    else:
        info(f"MinIO 文件删除完成，释放空间约 {human_size(freed)}")

    # ── 删除数据库专辑记录（级联删除曲目/评论/收藏/购物车等） ──
    try:
        album_ids = [item["album_id"] for item in plan]
        for aid in album_ids:
            cur.execute("DELETE FROM albums WHERE album_id = %s", (aid,))
        conn.commit()
        info(f"数据库记录删除完成：{len(album_ids)} 张专辑及其关联的曲目、评论、收藏、购物车等记录已删除。")
        print("  （社团 circles 与用户 users 数据未受影响）")
    except Exception as exc:
        conn.rollback()
        error(f"数据库删除失败：{exc}")
        error(f"请手动删除以下专辑：{album_ids}")
        conn.close()
        return 1

    # ── 清理后重新统计 ─────────────────────────
    print()
    try:
        cur.execute("SELECT pg_database_size(%s)", (db_name,))
        new_db_size = int(cur.fetchone()[0])
    except Exception:
        new_db_size = None
    try:
        new_minio_total = sum(
            obj.size for obj in client.list_objects(bucket, recursive=True)
        )
    except Exception:
        new_minio_total = None

    print("  清理后存储占用：")
    if new_db_size is not None:
        print(f"    PostgreSQL 数据库：{human_size(new_db_size)}")
    if new_minio_total is not None:
        print(f"    MinIO 存储卷：{human_size(new_minio_total)}")
    if new_db_size is not None and new_minio_total is not None:
        print(f"    项目总占用：{human_size(new_db_size + new_minio_total)}")

    print()
    info("存储检测与专辑清理流程结束。")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
