"""统一延迟控制器。

所有延迟逻辑统一走此模块，禁止在 spider 中直接 time.sleep()。
"""

from __future__ import annotations

import logging
import random
import time

logger = logging.getLogger(__name__)


def _get_reactor():
    """获取 Twisted reactor（延迟导入，便于测试 mock）。"""
    from twisted.internet import reactor
    return reactor


def schedule_album_delay(min_sec: int, rand_sec: int, callback) -> None:
    """专辑间延迟：固定最小秒数 + 随机 0~rand_sec 秒，不阻塞 reactor。

    Args:
        min_sec: 最小延迟秒数
        rand_sec: 随机额外秒数上限
        callback: 延迟结束后的回调函数
    """
    wait = min_sec + random.randint(0, rand_sec)
    logger.info("专辑间延迟 %ds（min=%d + rand(%d)）", wait, min_sec, rand_sec)
    _get_reactor().callLater(wait, callback)


def schedule_track_delay(min_sec: int, rand_max: int) -> None:
    """曲目间延迟：固定最小秒数 + 随机 0~rand_max 秒。

    注意：此函数使用 time.sleep 阻塞当前线程。
    在 Scrapy 回调中调用会阻塞 reactor —— 这是有意为之的设计，
    因为曲目音频下载（requests.get）本身已是同步阻塞。
    如需非阻塞延迟，应重构音频下载为 Twisted deferred。
    """
    delay = min_sec + random.randint(0, rand_max)
    if delay > 0:
        time.sleep(delay)


def schedule_circle_delay(delay_sec: int, callback) -> None:
    """社团间延迟：固定秒数，不阻塞 reactor。

    Args:
        delay_sec: 延迟秒数
        callback: 延迟结束后的回调函数
    """
    logger.info("社团间延迟 %ds", delay_sec)
    _get_reactor().callLater(delay_sec, callback)
