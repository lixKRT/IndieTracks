"""
album_test — 测试爬虫：从 API 取 10 张专辑，逐张爬取关联数据。

用法：
    scrapy crawl album_test
"""

from __future__ import annotations

import logging

import scrapy

from indietracks_spider.spiders.album_base import BaseAlbumSpider
from indietracks_spider.utils.config_loader import get_delay_config
from indietracks_spider.utils.constants import BASE

logger = logging.getLogger(__name__)


class AlbumTestSpider(BaseAlbumSpider):
    name = "album_test"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        delay_cfg = get_delay_config()
        self._track_min = delay_cfg.get("between_tracks_min", 1)
        self._track_random_max = delay_cfg.get("between_tracks_random_max", 3)

    async def start(self):
        yield self.make_disc_request(0, self.parse_disc_list)

    def parse_disc_list(self, response):
        discs = self._parse_discs_response(response)
        if discs is None:
            return
        self.logger.info("获取到 %d 张专辑，开始逐张处理", len(discs))

        for disc in discs:
            slug = disc["id"]
            self.logger.info("[%s] 开始处理: %s", slug, disc.get("title", "?"))
            yield scrapy.Request(
                f"{BASE}/d/{slug}/",
                callback=self.parse_album_detail,
                meta={"disc": disc},
                dont_filter=True,
            )
