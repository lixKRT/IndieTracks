"""
user_pages — 用户维页面爬虫

爬取 /u/{id}/music/ (已购) / /u/{id}/likes/ (收藏) / /u/{id}/following/ (关注社团)。
遵守 spider.json 的 mode 和 max_users 控制。支持 -a user_ids=1,2,3 覆盖 DB 读取。

用法：
    scrapy crawl user_pages                        # 从 DB 取用户
    scrapy crawl user_pages -a user_ids=2,3,5      # 指定用户
"""

import logging
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote

import scrapy

from indietracks_spider.items import (
    FavoriteItem,
    OwnedAlbumItem,
    CircleFollowItem,
)
from indietracks_spider.utils.config_loader import (
    get_delay_config,
    get_spider_config,
)
from indietracks_spider.utils.constants import BASE
from indietracks_spider.utils.db import get_connection, close_connection
from indietracks_spider.utils.parsing import check_response_ok

logger = logging.getLogger(__name__)

# 分页参数：music 用 ?page=，likes/following 用 ?dp=
PAGE_PARAM = {"music": "page", "likes": "dp", "following": "dp"}


class UserPagesSpider(scrapy.Spider):
    name = "user_pages"

    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        spider_cfg = get_spider_config()
        self._mode = spider_cfg.get("mode", "full")
        self._max_users = spider_cfg.get("max_users", 20)

        # -a user_ids= 命令行覆盖
        raw = kwargs.get("user_ids") or ""
        raw = raw.strip()
        self._target_user_ids = [
            int(x.strip()) for x in raw.split(",") if x.strip().isdigit()
        ] if raw else None

        self._db_conn = None
        self._db_cur = None

        self._processed = 0
        self._skipped = 0
        self._processed_uids: set[int] = set()

        delay_cfg = get_delay_config()
        self._download_delay = delay_cfg.get("download_delay", 3)

        self.logger.info(
            "user_pages 启动 | mode=%s | max_users=%s | target_user_ids=%s",
            self._mode,
            self._max_users if self._max_users else "无限制",
            self._target_user_ids if self._target_user_ids else "DB读取",
        )

    # ── DB ────────────────────────────────────────────

    def _ensure_db(self):
        if self._db_cur is not None:
            return
        self._db_conn, self._db_cur = get_connection()

    def _get_users(self):
        """从 DB 读取待处理用户列表。"""
        self._ensure_db()

        if self._target_user_ids:
            placeholders = ",".join(["%s"] * len(self._target_user_ids))
            self._db_cur.execute(
                f"SELECT dizzylab_user_id, username FROM users WHERE dizzylab_user_id IN ({placeholders}) ORDER BY dizzylab_user_id",
                tuple(self._target_user_ids),
            )
            users = self._db_cur.fetchall()
            self.logger.info("指定用户 %d 人，实际找到 %d 人", len(self._target_user_ids), len(users))
        else:
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            if self._mode == "incremental":
                self._db_cur.execute(
                    """SELECT dizzylab_user_id, username FROM users
                       WHERE userpage_crawled_at IS NULL
                          OR userpage_crawled_at < %s
                       ORDER BY dizzylab_user_id""",
                    (cutoff,),
                )
            else:
                self._db_cur.execute(
                    "SELECT dizzylab_user_id, username FROM users ORDER BY dizzylab_user_id"
                )
            users = self._db_cur.fetchall()
            self.logger.info("从 DB 读取到 %d 个用户", len(users))

        return users

    def _resolve_album_id(self, dizzylab_id: str, title: str | None = None) -> int | None:
        """查找或创建 album 占位行，返回 album_id。"""
        self._ensure_db()
        self._db_cur.execute(
            "SELECT album_id FROM albums WHERE dizzylab_id = %s",
            (dizzylab_id,),
        )
        row = self._db_cur.fetchone()
        if row:
            return row[0]
        self._db_cur.execute(
            """INSERT INTO albums (dizzylab_id, title) VALUES (%s, %s)
               ON CONFLICT (dizzylab_id) DO NOTHING
               RETURNING album_id""",
            (dizzylab_id, title or dizzylab_id),
        )
        row = self._db_cur.fetchone()
        return row[0] if row else None

    def _resolve_circle_id(self, name: str) -> int | None:
        """根据社团名查找 circle_id。"""
        self._ensure_db()
        self._db_cur.execute(
            "SELECT circle_id FROM circles WHERE name = %s",
            (name,),
        )
        row = self._db_cur.fetchone()
        return row[0] if row else None

    def _resolve_user_db_id(self, dizzylab_user_id: int) -> int | None:
        """查找 user_id（db 主键）。"""
        self._ensure_db()
        self._db_cur.execute(
            "SELECT user_id FROM users WHERE dizzylab_user_id = %s",
            (dizzylab_user_id,),
        )
        row = self._db_cur.fetchone()
        return row[0] if row else None

    def _mark_user_crawled(self, dizzylab_user_id: int):
        self._ensure_db()
        self._db_cur.execute(
            "UPDATE users SET userpage_crawled_at = %s WHERE dizzylab_user_id = %s",
            (datetime.now(timezone.utc), dizzylab_user_id),
        )

    def closed(self, reason):
        # 标记所有已处理的用户
        for uid in self._processed_uids:
            self._mark_user_crawled(uid)

        close_connection(self._db_conn, self._db_cur)
        self.logger.info(
            "user_pages 结束 | processed=%d | skipped=%d | reason=%s",
            self._processed,
            self._skipped,
            reason,
        )

    # ── 入口 ──────────────────────────────────────────

    def start_requests(self):
        users = self._get_users()
        limit = self._max_users if self._max_users > 0 else None

        for dizzylab_uid, username in users:
            if limit is not None and self._processed + self._skipped >= limit:
                self.logger.info("已达 max_users=%d，停止", self._max_users)
                break

            # incremental 模式下，查页面是否已存在数据
            if self._mode == "incremental":
                self._ensure_db()
                self._db_cur.execute(
                    "SELECT userpage_crawled_at FROM users WHERE dizzylab_user_id = %s",
                    (dizzylab_uid,),
                )
                row = self._db_cur.fetchone()
                if row and row[0]:
                    age = datetime.now(timezone.utc) - row[0].replace(tzinfo=timezone.utc)
                    if age.days < 30:
                        self._skipped += 1
                        self.logger.info("[跳过: %d] %s (uid=%d) 30天内已爬", self._skipped, username, dizzylab_uid)
                        continue

            self._processed += 1
            self.logger.info(
                "[%d] %s (uid=%d) | mode=%s | 跳过: %d",
                self._processed,
                username,
                dizzylab_uid,
                self._mode,
                self._skipped,
            )

            meta = {"_dizzylab_user_id": dizzylab_uid, "_username": username}
            self._processed_uids.add(dizzylab_uid)

            # 三种页面的首页
            yield scrapy.Request(
                f"{BASE}/u/{dizzylab_uid}/music/?page=1",
                callback=self.parse_music,
                meta={**meta, "_page": 1},
                dont_filter=True,
            )
            yield scrapy.Request(
                f"{BASE}/u/{dizzylab_uid}/likes/?dp=1",
                callback=self.parse_likes,
                meta={**meta, "_dp": 1},
                dont_filter=True,
            )
            yield scrapy.Request(
                f"{BASE}/u/{dizzylab_uid}/following/?dp=1",
                callback=self.parse_following,
                meta={**meta, "_dp": 1},
                dont_filter=True,
            )

    # ── 通用：提取分页最大页码 ───────────────────────

    @staticmethod
    def _max_page(response, param: str) -> int:
        """从 pagination 组件提取最大页码。"""
        pages = set()
        for href in response.xpath(
            f"//ul[contains(@class,'pagination')]//a[contains(@href,'{param}=')]/@href"
        ).getall():
            m = re.search(rf'{param}=(\d+)', href)
            if m:
                pages.add(int(m.group(1)))
        return max(pages) if pages else 1

    # ── Music：已购专辑 ───────────────────────────────

    def parse_music(self, response):
        if not check_response_ok(response):
            return
        dizzylab_uid = response.meta["_dizzylab_user_id"]
        current_page = response.meta["_page"]
        user_db_id = self._resolve_user_db_id(dizzylab_uid)

        if not user_db_id:
            self.logger.warning("用户 %d 不在 DB 中，跳过 music 解析", dizzylab_uid)
            return

        for slug, title in self._parse_album_cards(response):
            album_id = self._resolve_album_id(slug, title)
            if not album_id:
                continue
            oa = OwnedAlbumItem()
            oa["user_id"] = user_db_id
            oa["album_id"] = album_id
            yield oa

        # 翻页
        max_p = self._max_page(response, "page")
        if current_page < max_p:
            yield scrapy.Request(
                f"{BASE}/u/{dizzylab_uid}/music/?page={current_page + 1}",
                callback=self.parse_music,
                meta={"_dizzylab_user_id": dizzylab_uid, "_page": current_page + 1},
                dont_filter=True,
            )

    # ── Likes：收藏 ───────────────────────────────────

    def parse_likes(self, response):
        if not check_response_ok(response):
            return
        dizzylab_uid = response.meta["_dizzylab_user_id"]
        current_dp = response.meta["_dp"]
        user_db_id = self._resolve_user_db_id(dizzylab_uid)

        if not user_db_id:
            return

        for slug, title in self._parse_album_cards(response):
            album_id = self._resolve_album_id(slug, title)
            if not album_id:
                continue
            fav = FavoriteItem()
            fav["user_id"] = user_db_id
            fav["album_id"] = album_id
            yield fav

        # 翻页
        max_p = self._max_page(response, "dp")
        if current_dp < max_p:
            yield scrapy.Request(
                f"{BASE}/u/{dizzylab_uid}/likes/?dp={current_dp + 1}",
                callback=self.parse_likes,
                meta={"_dizzylab_user_id": dizzylab_uid, "_dp": current_dp + 1},
                dont_filter=True,
            )

    # ── Following：关注社团 ────────────────────────────

    def parse_following(self, response):
        if not check_response_ok(response):
            return
        dizzylab_uid = response.meta["_dizzylab_user_id"]
        current_dp = response.meta["_dp"]
        user_db_id = self._resolve_user_db_id(dizzylab_uid)

        if not user_db_id:
            return

        for name in self._parse_circle_names(response):
            circle_id = self._resolve_circle_id(name)
            if not circle_id:
                self.logger.info("  社团 '%s' 不在 circles 表中，跳过", name)
                continue
            cf = CircleFollowItem()
            cf["user_id"] = user_db_id
            cf["circle_id"] = circle_id
            yield cf

        # 翻页
        max_p = self._max_page(response, "dp")
        if current_dp < max_p:
            yield scrapy.Request(
                f"{BASE}/u/{dizzylab_uid}/following/?dp={current_dp + 1}",
                callback=self.parse_following,
                meta={"_dizzylab_user_id": dizzylab_uid, "_dp": current_dp + 1},
                dont_filter=True,
            )

    # ── HTML 解析辅助 ─────────────────────────────────

    @staticmethod
    def _parse_album_cards(response):
        """music / likes 页面通用：提取 (slug, title) 列表。"""
        results = []
        for a in response.xpath("//div[@id='discs' or @id='album']//a[contains(@href, '/d/')]"):
            href = a.xpath("./@href").get("")
            m = re.search(r"/d/([^/]+)", href)
            if not m:
                continue
            slug = m.group(1)
            title = a.xpath(
                "ancestor::div[contains(@class,'card')]"
                "//p[contains(@class,'text-truncate')]/text()"
            ).get()
            results.append((slug, (title or "").strip()))
        return results

    @staticmethod
    def _parse_circle_names(response):
        """following 页面：提取 circle 名称列表（URL 解码）。"""
        names = set()
        for a in response.xpath(
            "//div[contains(@class,'tab-pane')]//a[contains(@href, '/l/')]"
        ):
            href = a.xpath("./@href").get("")
            m = re.search(r"/l/([^/]+)", href)
            if m:
                names.add(unquote(m.group(1)))
        return list(names)
