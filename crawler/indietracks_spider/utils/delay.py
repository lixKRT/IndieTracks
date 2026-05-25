"""
统一延迟控制器。

提供 between_albums_sleep() 和 between_tracks_sleep()。
所有蜘蛛统一调用，避免延迟逻辑分散。
"""

import random
import time
import logging
from typing import Any

logger = logging.getLogger(__name__)


def between_albums_sleep(min_sec: int, rand_sec: int) -> None:
    """专辑间延迟：固定最小秒数 + 随机 0~rand_sec 秒。"""
    wait = min_sec + random.randint(0, rand_sec)
    logger.info("专辑间延迟 %ds（min=%d + rand(%d)）", wait, min_sec, rand_sec)
    time.sleep(wait)


def between_tracks_sleep(min_sec: int, rand_max: int) -> None:
    """曲目间延迟：固定最小秒数 + 随机 0~rand_max 秒。"""
    delay = min_sec + random.randint(0, rand_max)
    if delay > 0:
        time.sleep(delay)
