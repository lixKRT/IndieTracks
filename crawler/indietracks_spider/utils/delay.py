"""
专辑间延迟控制器。

在 Spider 中每处理完一张专辑的全部子请求后调用：
    between_albums_sleep(delay_cfg)
"""
import random
import time
import logging
from typing import Any

logger = logging.getLogger(__name__)


def between_albums_sleep(delay_cfg: dict[str, Any]) -> None:
    """每张专辑处理完后等待指定时间（最小 + 随机）。"""
    min_sec = delay_cfg.get("between_albums_min", 60)
    rand_sec = delay_cfg.get("between_albums_random", 60)
    wait = min_sec + random.randint(0, rand_sec)
    logger.info(
        "专辑间延迟 %d 秒（min=%ds + random(0,%ds)）",
        wait, min_sec, rand_sec,
    )
    time.sleep(wait)
