"""Scrapy settings — 从 config JSON 动态加载。"""

import sys
from pathlib import Path

# 确保 crawler/ 在路径中，以便 import indietracks_spider.*
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from indietracks_spider.utils.config_loader import get_delay_config

BOT_NAME = "indietracks_spider"
SPIDER_MODULES = ["indietracks_spider.spiders"]
NEWSPIDER_MODULE = "indietracks_spider.spiders"

# ── 延迟策略（从 config/delay.json 读取） ──────────────────
_delay = get_delay_config()

DOWNLOAD_DELAY = _delay["download_delay"]
CONCURRENT_REQUESTS_PER_DOMAIN = _delay["concurrent_requests_per_domain"]

# ── 基础反爬 ──────────────────────────────────────────────
ROBOTSTXT_OBEY = False  # dizzylab robots.txt 禁用 /*?* 导致 API 全被封
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
