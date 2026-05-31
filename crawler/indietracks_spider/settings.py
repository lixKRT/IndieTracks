"""Scrapy settings — 延迟加载 config JSON，支持测试注入。"""

from __future__ import annotations

import sys
from pathlib import Path

# 确保 crawler/ 在路径中，以便 import indietracks_spider.*
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BOT_NAME = "indietracks_spider"
SPIDER_MODULES = ["indietracks_spider.spiders"]
NEWSPIDER_MODULE = "indietracks_spider.spiders"

# ── 延迟策略（延迟加载，支持测试注入）─────────────────────

def _get_delay():
    """延迟加载 delay config，避免 import 时读文件。"""
    from indietracks_spider.utils.config_loader import get_delay_config
    return get_delay_config()


def _lazy_setting(key: str, default=None):
    """延迟读取配置项。"""
    return _get_delay().get(key, default)


# 使用 property-style 延迟加载
DOWNLOAD_DELAY = property(lambda self: _lazy_setting("download_delay"))
CONCURRENT_REQUESTS_PER_DOMAIN = property(lambda self: _lazy_setting("concurrent_requests_per_domain"))

# 直接赋值（Scrapy settings 需要非 descriptor 值）
# 通过 from_crawler 或 spider custom_settings 覆盖
_delay_cache = None

def _ensure_delay():
    global _delay_cache
    if _delay_cache is None:
        _delay_cache = _get_delay()
    return _delay_cache


class _LazySettings:
    """让 DOWNLOAD_DELAY 等在首次访问时才读配置。"""

    def __init__(self):
        self._cache = {}

    def __getitem__(self, key):
        if key not in self._cache:
            from indietracks_spider.utils.config_loader import get_delay_config
            cfg = get_delay_config()
            self._cache = cfg
        return self._cache.get(key)


# Scrapy 要求模块级变量，先给默认值，spider custom_settings 覆盖
DOWNLOAD_DELAY = 3
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# ── 基础反爬 ──────────────────────────────────────────────
ROBOTSTXT_OBEY = False
COOKIES_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# ── Pipeline ──────────────────────────────────────────────
ITEM_PIPELINES = {
    "indietracks_spider.pipelines.PostgresPipeline": 300,
}

# ── 日志 ──────────────────────────────────────────────────
LOG_LEVEL = "INFO"

# ── 其他 ──────────────────────────────────────────────────
FEED_EXPORT_ENCODING = "utf-8"
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
