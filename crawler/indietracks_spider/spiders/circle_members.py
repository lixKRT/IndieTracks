"""
circle_members — 社团成员爬虫

遍历 circles 表所有社团，逐社团爬取成员列表。遵守 spider.json 的 mode 控制。
社团间隔使用 Twisted reactor.callLater，不阻塞引擎。

用法：
    scrapy crawl circle_members
"""

import logging
from urllib.parse import quote

import scrapy
from scrapy.exceptions import DontCloseSpider
from scrapy import signals

from indietracks_spider.items import UserItem, UserCircleItem
from indietracks_spider.utils.config_loader import (
    get_delay_config,
    get_spider_config,
)
from indietracks_spider.utils.constants import BASE
from indietracks_spider.utils.db import get_connection, close_connection
from indietracks_spider.utils.parsing import extract_user_id, check_response_ok

logger = logging.getLogger(__name__)


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

        # 队列驱动
        self._pending_circles: list[tuple] = []

        self._delay_pending = False

        self.logger.info(
            "circle_members 启动 | mode=%s | 社团间延迟=%ds",
            self._mode,
            self._circle_delay,
        )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider._spider_idle, signal=signals.spider_idle)
        return spider

    def _spider_idle(self):
        if self._delay_pending or self._pending_circles:
            raise DontCloseSpider

    def _ensure_db(self):
        if self._db_cur is not None:
            return
        self._db_conn, self._db_cur = get_connection()

    def _circle_members_up_to_date(self, circle_id: int) -> bool:
        self._ensure_db()
        self._db_cur.execute(
            """SELECT c.member_count, COUNT(uc.user_id)
               FROM circles c
               LEFT JOIN user_circles uc ON uc.circle_id = c.circle_id
               WHERE c.circle_id = %s
               GROUP BY c.circle_id""",
            (circle_id,),
        )
        row = self._db_cur.fetchone()
        if row is None:
            return False
        stored_count, actual_count = row
        return stored_count is not None and stored_count == actual_count

    def closed(self, reason):
        close_connection(self._db_conn, self._db_cur)
        self.logger.info(
            "circle_members 结束 | processed=%d | skipped=%d | reason=%s",
            self._processed,
            self._skipped,
            reason,
        )

    # ── 调度 ─────────────────────────────────────────

    def _schedule_next(self):
        """取下一个待处理社团，注入引擎。"""
        while self._pending_circles:
            circle_id, dizzylab_labelid, name = self._pending_circles.pop(0)

            if self._mode == "incremental" and self._circle_members_up_to_date(circle_id):
                self._skipped += 1
                self.logger.info("[跳过: %d] %s (circle_id=%d) 成员数无变化", self._skipped, name, circle_id)
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

            self.crawler.engine.crawl(
                scrapy.Request(
                    f"{BASE}/l/{quote(name)}/",
                    callback=self.parse_circle_detail,
                    meta={
                        "_circle_id": circle_id,
                        "_dizzylab_labelid": dizzylab_labelid,
                        "_circle_name": name,
                    },
                    dont_filter=True,
                ),
            )
            return

    # ── 入口 ─────────────────────────────────────────

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
        self._pending_circles = list(circles)
        self._schedule_next()
        yield from ()  # 请求由 engine.crawl() 注入，start() 需要可迭代对象

    # ── 解析社团详情页 ──────────────────────────────

    def parse_circle_detail(self, response):
        if not check_response_ok(response):
            self.logger.warning("社团详情页异常，跳过")
            self._delay_pending = True
            from twisted.internet import reactor
            reactor.callLater(self._circle_delay, self._on_delay_done)
            return
        circle_id = response.meta["_circle_id"]
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

        self._ensure_db()
        self._db_cur.execute(
            "UPDATE circles SET member_count = %s WHERE circle_id = %s",
            (found, circle_id),
        )

        # 社团间延迟（不阻塞 reactor）
        self._delay_pending = True
        from twisted.internet import reactor
        reactor.callLater(self._circle_delay, self._on_delay_done)

    def _on_delay_done(self):
        self._delay_pending = False
        self._schedule_next()
