"""
album_test — 测试爬虫：从 API 取 10 张专辑，逐张爬取关联数据。

用法：
    scrapy crawl album_test
"""

import logging

import scrapy

from indietracks_spider.spiders.album_base import BaseAlbumSpider
from indietracks_spider.utils.config_loader import get_delay_config
from indietracks_spider.utils.constants import BASE, API_DISCS
from indietracks_spider.utils.parsing import safe_json_load, check_response_ok

logger = logging.getLogger(__name__)


class AlbumTestSpider(BaseAlbumSpider):
    name = "album_test"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        delay_cfg = get_delay_config()
        self._track_min = delay_cfg.get("between_tracks_min", 1)
        self._track_random_max = delay_cfg.get("between_tracks_random_max", 3)

    def start_requests(self):
        url = f"{API_DISCS}?l=0&r=10&sort=ad&type=album"
        yield scrapy.Request(url, callback=self.parse_disc_list)

    def parse_disc_list(self, response):
        if not check_response_ok(response):
            return
        data = safe_json_load(response)
        if data is None:
            return
        discs = data.get("discs", [])
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
