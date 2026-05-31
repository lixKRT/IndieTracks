"""
album_bulk — 批量爬虫

用途：首次数据铺底 + 全量刷新。遵守 spider.json 的 mode / max_albums 控制。
专辑间隔使用 Twisted reactor.callLater，不阻塞引擎。

用法：
    scrapy crawl album_bulk
"""

from __future__ import annotations

import logging

import scrapy
from scrapy.exceptions import DontCloseSpider
from scrapy import signals

from indietracks_spider.spiders.album_base import BaseAlbumSpider
from indietracks_spider.utils.config_loader import (
    get_delay_config,
    get_spider_config,
)
from indietracks_spider.utils.constants import BASE, PAGE_SIZE
from indietracks_spider.utils.delay import schedule_album_delay

logger = logging.getLogger(__name__)


class AlbumBulkSpider(BaseAlbumSpider):
    name = "album_bulk"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        spider_cfg = get_spider_config()
        self._mode = spider_cfg.get("mode", "full")
        self._max_albums = spider_cfg.get("max_albums", 0)

        delay_cfg = get_delay_config()
        self._between_min = delay_cfg.get("between_albums_min", 60)
        self._between_random = delay_cfg.get("between_albums_random", 60)
        self._track_min = delay_cfg.get("between_tracks_min", 1)
        self._track_random_max = delay_cfg.get("between_tracks_random_max", 5)

        self._processed = 0
        self._skipped = 0

        # 队列驱动
        self._pending_discs: list[dict] = []
        self._next_page = 0
        self._fetching = False
        self._started = False
        self._delay_pending = False
        self._just_fetched = False

        self.logger.info(
            "album_bulk 启动 | mode=%s | max_albums=%s | between=%d+rand(0,%d)s",
            self._mode,
            self._max_albums if self._max_albums > 0 else "∞",
            self._between_min,
            self._between_random,
        )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider._spider_idle, signal=signals.spider_idle)
        return spider

    def _spider_idle(self):
        """引擎空闲时触发——启动专辑间延迟并保持引擎存活。"""
        if self._delay_pending or self._fetching:
            raise DontCloseSpider
        if self._pending_discs:
            if self._just_fetched:
                self._just_fetched = False
                self._process_next_disc()
            else:
                self._delay_pending = True
                schedule_album_delay(self._between_min, self._between_random, self._on_delay_done)
            raise DontCloseSpider
        # 无待处理专辑，检查是否需要翻页
        if self._max_albums == 0 or self._processed < self._max_albums:
            self._fetching = True
            self._just_fetched = True
            next_start = self._next_page + PAGE_SIZE
            self._next_page = next_start
            self.logger.info("队列空，翻页 l=%d", next_start)
            self.crawler.engine.crawl(
                self.make_disc_request(next_start, self.parse_disc_list, meta={"page_start": next_start})
            )
            raise DontCloseSpider

    def closed(self, reason):
        super().closed(reason)
        self.logger.info(
            "album_bulk 结束 | processed=%d | skipped=%d | reason=%s",
            self._processed,
            self._skipped,
            reason,
        )

    # ── 入口 ─────────────────────────────────────────

    async def start(self):
        yield self.make_disc_request(0, self.parse_disc_list, meta={"page_start": 0})

    # ── 调度核心 ─────────────────────────────────────

    def _process_next_disc(self):
        """从队列取出下一张专辑并注入引擎。"""
        if self._pending_discs:
            disc = self._pending_discs.pop(0)
            slug = disc["id"]
            self.logger.info("  [调度] 注入专辑请求: %s", slug)
            self.crawler.engine.crawl(
                scrapy.Request(
                    f"{BASE}/d/{slug}/",
                    callback=self.parse_album_detail,
                    meta={"disc": disc},
                    dont_filter=True,
                ),
            )

    # ── 翻页处理 ─────────────────────────────────────

    def parse_disc_list(self, response):
        self._fetching = False
        discs = self._parse_discs_response(response)
        if discs is None:
            return
        page_start = response.meta["page_start"]

        if not discs:
            self.logger.info("API 返回 0 条数据，翻页结束")
            return

        self.logger.info("翻页 l=%d，获取到 %d 张专辑", page_start, len(discs))

        page_processed = 0

        for disc in discs:
            if self._max_albums > 0 and self._processed >= self._max_albums:
                self.logger.info("已达上限 %d 张，停止翻页", self._max_albums)
                break

            slug = disc["id"]
            complete = self._album_is_complete(slug)

            if complete:
                self._skipped += 1
                self.logger.info(
                    "[%s] 跳过 | 数据完整 | 累计跳过: %d",
                    slug,
                    self._skipped,
                )
                continue

            self._processed += 1
            page_processed += 1
            max_str = str(self._max_albums) if self._max_albums > 0 else "∞"

            self.logger.info(
                "[%d/%s] %s - %s ✓ | mode=%s | 跳过: %d",
                self._processed,
                max_str,
                slug,
                disc.get("title", "?"),
                self._mode,
                self._skipped,
            )
            self._pending_discs.append(disc)

        # 增量模式：整页全跳过则继续翻下一页
        if self._mode == "incremental" and page_processed == 0:
            self.logger.info("增量模式：本页无待处理专辑，翻下一页")

        # 首次触发：直接 yield 第一张
        if not self._started:
            self._started = True
            if self._pending_discs:
                disc = self._pending_discs.pop(0)
                slug = disc["id"]
                self.logger.info("  [调度] 首张专辑: %s", slug)
                yield scrapy.Request(
                    f"{BASE}/d/{slug}/",
                    callback=self.parse_album_detail,
                    meta={"disc": disc},
                    dont_filter=True,
                )

    # ── 专辑间延迟 ──────────────────────────────────

    def _on_delay_done(self):
        """延迟结束，调度下一张专辑。"""
        self._delay_pending = False
        self._process_next_disc()
