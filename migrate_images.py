"""将 CDN 图片迁移到 MinIO 并更新数据库 URL。"""
import subprocess
import urllib.request
import os
import sys

# MinIO 配置
MINIO_ENDPOINT = "http://localhost:9000"
MINIO_BUCKET = "indietracks"
MC_EXE = r"E:\Project\IndieTracks\tools\minio\mc.exe"

# PostgreSQL 配置
PG_HOST = "localhost"
PG_PORT = "5432"
PG_DB = "indietracks"
PG_USER = "postgres"
PG_PASS = "54610"
PSQL = r"C:\Program Files\PostgreSQL\17\bin\psql.exe"

TEMP_DIR = r"E:\Project\IndieTracks\database\temp_images"


def run_sql(sql):
    env = {**os.environ, "PGPASSWORD": PG_PASS, "PGCLIENTENCODING": "UTF-8"}
    result = subprocess.run(
        [PSQL, "-h", PG_HOST, "-p", PG_PORT, "-U", PG_USER, "-d", PG_DB, "-t", "-A", "-c", sql],
        capture_output=True, env=env
    )
    return result.stdout.decode("utf-8", errors="replace").strip()


def download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    urllib.request.urlretrieve(url, dest)


def upload_to_minio(local_path, object_key):
    result = subprocess.run(
        [MC_EXE, "cp", local_path, f"local/{MINIO_BUCKET}/{object_key}"],
        capture_output=True, text=True
    )
    return result.returncode == 0


def migrate_table(table, url_column, id_column, prefix):
    rows = run_sql(f"SELECT {id_column}, {url_column} FROM {table} WHERE {url_column} IS NOT NULL AND {url_column} LIKE 'https://cdn.dizzylab.net%';")
    if not rows:
        print(f"  No CDN URLs in {table}")
        return 0

    count = 0
    for line in rows.split("\n"):
        if not line.strip():
            continue
        parts = line.split("|", 1)
        if len(parts) != 2:
            continue
        row_id, url = parts[0].strip(), parts[1].strip()
        if not url:
            continue

        # 从 URL 提取文件名
        filename = url.split("/")[-1].split("!")[0]  # 去掉 !cover 后缀
        object_key = f"{prefix}/{filename}"
        local_path = os.path.join(TEMP_DIR, prefix, filename)

        try:
            print(f"  [{table}] {row_id}: {filename}")
            download(url, local_path)
            if upload_to_minio(local_path, object_key):
                new_url = f"{MINIO_ENDPOINT}/{MINIO_BUCKET}/{object_key}"
                run_sql(f"UPDATE {table} SET {url_column} = '{new_url}' WHERE {id_column} = {row_id};")
                count += 1
            else:
                print(f"    WARN: upload failed")
        except Exception as e:
            print(f"    ERROR: {e}")

    return count


def main():
    print("=" * 50)
    print("  Image Migration: CDN → MinIO")
    print("=" * 50)

    os.makedirs(TEMP_DIR, exist_ok=True)

    print("\n[1/3] Album covers...")
    c1 = migrate_table("albums", "cover_url", "album_id", "covers")
    print(f"  Done: {c1} covers migrated")

    print("\n[2/3] Circle logos...")
    c2 = migrate_table("circles", "logo_url", "circle_id", "logos")
    print(f"  Done: {c2} logos migrated")

    print("\n[3/3] User avatars...")
    c3 = migrate_table("users", "avatar_url", "user_id", "avatars")
    print(f"  Done: {c3} avatars migrated")

    print(f"\nTotal: {c1 + c2 + c3} images migrated")

    # 清理临时文件
    import shutil
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    print("Temp files cleaned up.")


if __name__ == "__main__":
    main()
