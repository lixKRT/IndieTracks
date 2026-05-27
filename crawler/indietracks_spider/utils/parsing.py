"""共享解析函数。"""

import json
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


def safe_json_load(response) -> dict | None:
    """安全解析 JSON 响应，失败返回 None。"""
    try:
        return json.loads(response.text)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("JSON 解析失败: %s (%s)", response.url, e)
        return None


def check_response_ok(response) -> bool:
    """检查 HTTP 响应状态是否为 2xx，非 200 打 warning 并返回 False。"""
    if response.status >= 400:
        logger.warning("HTTP %d: %s", response.status, response.url)
        return False
    return True


def extract_user_id(url: str) -> int | None:
    """从 Dizzylab URL 提取数字 user_id。"""
    m = re.search(r"/u/(\d+)|/albums/u/(\d+)", url)
    return int(m.group(1) or m.group(2)) if m else None


def parse_date_cn(text: str) -> datetime | None:
    """解析"2026年5月1日" → datetime。"""
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def parse_track_title(title_text: str) -> tuple[str, str]:
    """解析曲目标题文本 → (file_name, track_length)。"""
    from indietracks_spider.utils.constants import TRACK_RE

    m = TRACK_RE.match(title_text.strip())
    if m:
        return m.group(1).strip(), m.group(2)
    return title_text.strip(), ""
