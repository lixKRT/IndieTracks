"""
circle_members — 社团成员爬虫

遍历 circles 表所有社团，逐社团爬取成员列表。遵守 spider.json 的 mode 控制。

用法：
    scrapy crawl circle_members
"""

import logging
import random
import re
import time

import psycopg2
import scrapy
from scrapy.exceptions import CloseSpider

from indietracks_spider.items import UserItem, UserCircleItem
from indietracks_spider.utils.config_loader import (
    get_database_config,
    get_delay_config,
    get_spider_config,
)

logger = logging.getLogger(__name__)

BASE = "https://www.dizzylab.net"


def extract_user_id(url: str) -> int | None:
    m = re.search(r"/u/(\d+)|/albums/u/(\d+)", url)
    return int(m.group(1) or m.group(2)) if m else None


class CircleMembersSpider(scrapy.Spider):
    name = "circle_members"

    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        spider_cfg = get_spider_config()
        self._mode = spider_cfg.get("mode", "full")

        delay_cfg = get_delay_config()
        self._circle_delay = delay_cfg.get("download_delay", 3)

        self._processed = 0
        self._skipped = 0
        self._db_conn = None
        self._db_cur = None

        self.logger.info(
            "circle_members 启动 | mode=%s | 社团间延迟=%ds",
            self._mode,
            self._circle_delay,
        )

    def _ensure_db(self):
        if self._db_cur is not None:
            return
        db = get_database_config()
        if not db.get("user"):
            raise RuntimeError("数据库未配置，请编辑 crawler/config/database.json")
        self._db_conn = psycopg2.connect(
            host=db["host"],
            port=db["port"],
            database=db["database"],
            user=db["user"],
            password=db["password"],
            options="-c client_encoding=UTF8",
        )
        self._db_conn.autocommit = True
        self._db_cur = self._db_conn.cursor()

    def _circle_has_members(self, circle_id: int) -> bool:
        self._ensure_db()
        self._db_cur.execute(
            "SELECT EXISTS(SELECT 1 FROM user_circles WHERE circle_id = %s)",
            (circle_id,),
        )
        return self._db_cur.fetchone()[0]

    def closed(self, reason):
        if self._db_cur:
            self._db_cur.close()
        if self._db_conn:
            self._db_conn.close()
        self.logger.info(
            "circle_members 结束 | processed=%d | skipped=%d | reason=%s",
            self._processed,
            self._skipped,
            reason,
        )

    # ── 入口：从数据库读取社团列表 ──────────────────

    def start_requests(self):
        self._ensure_db()
        self._db_cur.execute(
            "SELECT circle_id, dizzylab_labelid, name FROM circles ORDER BY circle_id"
        )
        circles = self._db_cur.fetchall()

        if not circles:
            self.logger.warning("circles 表为空，无社团可爬")
            return

        self.logger.info("从数据库读取到 %d 个社团", len(circles))

        for circle_id, dizzylab_labelid, name in circles:
            # incremental 模式：跳转已有成员的社团
            if self._mode == "incremental" and self._circle_has_members(circle_id):
                self._skipped += 1
                self.logger.info("[跳过: %d] %s (circle_id=%d) 已有成员", self._skipped, name, circle_id)
                continue

            self._processed += 1
            self.logger.info(
                "[%d] %s (circle_id=%d) | mode=%s | 跳过: %d",
                self._processed,
                name,
                circle_id,
                self._mode,
                self._skipped,
            )

            # URL 编码社团名
            from urllib.parse import quote
            circle_url = f"{BASE}/l/{quote(name)}/"
            yield scrapy.Request(
                circle_url,
                callback=self.parse_circle_detail,
                meta={
                    "_dizzylab_labelid": dizzylab_labelid,
                    "_circle_name": name,
                },
                dont_filter=True,
            )

    # ── 解析社团详情页 ──────────────────────────────

    def parse_circle_detail(self, response):
        labelid = response.meta["_dizzylab_labelid"]
        name = response.meta["_circle_name"]

        member_as = response.xpath(
            "//p[text()='成员']/following-sibling::div//a[contains(@href,'/u/')]"
        )

        found = 0
        for a in member_as:
            href = a.xpath("./@href").get("")
            uid = extract_user_id(href)
            title = a.xpath("./@title").get("")
            username = None
            if title:
                br_pos = title.rfind("<br>")
                if br_pos != -1:
                    username = title[br_pos + 4:].strip()
                else:
                    username = title.strip()

            if uid:
                u = UserItem()
                u["dizzylab_user_id"] = uid
                u["username"] = username
                u["user_role"] = "pro"
                yield u

                uc = UserCircleItem()
                uc["user_id"] = None
                uc["circle_id"] = None
                uc["_dizzylab_user_id"] = uid
                uc["_dizzylab_labelid"] = labelid
                yield uc
                found += 1

        self.logger.info("  %s: 找到 %d 名成员", name, found)

        # 社团间延迟（遵守 delay.json download_delay）
        time.sleep(self._circle_delay)
