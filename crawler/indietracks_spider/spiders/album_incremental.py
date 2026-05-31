"""
album_incremental — 增量爬虫

永远增量，不受 spider.json 控制。从 API 最新页开始翻，遇到第一条
数据完整的 dizzylab_id 立即停止。

用法：
    scrapy crawl album_incremental
"""

from __future__ import annotations

import logging

import scrapy
from scrapy.exceptions import CloseSpider

from indietracks_spider.spiders.album_base import BaseAlbumSpider
from indietracks_spider.utils.config_loader import get_delay_config
from indietracks_spider.utils.constants import BASE, PAGE_SIZE

logger = logging.getLogger(__name__)


class AlbumIncrementalSpider(BaseAlbumSpider):
    name = "album_incremental"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._captured = 0

        delay_cfg = get_delay_config()
        self._track_min = delay_cfg.get("between_tracks_min", 1)
        self._track_random_max = delay_cfg.get("between_tracks_random_max", 5)

        self.logger.info("album_incremental 启动 | 永远增量模式 | 遇到完整专辑即停")

    def closed(self, reason):
        super().closed(reason)
        self.logger.info(
            "album_incremental 结束 | captured=%d | reason=%s",
            self._captured,
            reason,
        )

    # ── 入口 ─────────────────────────────────────────

    async def start(self):
        yield self.make_disc_request(0, self.parse_disc_list, meta={"page_start": 0})

    # ── 翻页处理 ─────────────────────────────────────

    def parse_disc_list(self, response):
        discs = self._parse_discs_response(response)
        page_start = response.meta["page_start"]

        if discs is None:
            return
        if not discs:
            self.logger.info("API 返回 0 条数据，翻页结束")
            raise CloseSpider("数据源已耗尽")

        self.logger.info("翻页 l=%d，获取到 %d 张专辑", page_start, len(discs))

        for disc in discs:
            slug = disc["id"]

            if self._album_is_complete(slug):
                self.logger.info("遇到完整专辑 %s，停止", slug)
                raise CloseSpider(f"已追平最新数据（{slug} 已完整爬取）")

            self._captured += 1
            self.logger.info("[%d] %s - %s ✓", self._captured, slug, disc.get("title", "?"))

            yield scrapy.Request(
                f"{BASE}/d/{slug}/",
                callback=self.parse_album_detail,
                meta={"disc": disc},
                dont_filter=True,
            )

        next_start = page_start + PAGE_SIZE
        yield self.make_disc_request(next_start, self.parse_disc_list, meta={"page_start": next_start})
