"""MinIO 音频下载 + 上传工具。"""

import io
import logging

import requests
from minio import Minio

from indietracks_spider.utils.config_loader import get_minio_config

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
}

_client = None


def _get_client() -> Minio:
    global _client
    if _client is not None:
        return _client
    cfg = get_minio_config()
    endpoint = cfg["endpoint"].replace("http://", "").replace("https://", "")
    _client = Minio(
        endpoint,
        access_key=cfg["access_key"],
        secret_key=cfg["secret_key"],
        secure=False,
    )
    return _client


def download_and_upload(
    cdn_url: str,
    album_slug: str,
    sort_order: int,
) -> tuple[str, int] | None:
    """下载试听音频 → 上传 MinIO。

    Returns (object_key, file_size) 或 None（失败时跳过）。
    """
    cfg = get_minio_config()
    bucket = cfg["bucket"]
    prefix = cfg["prefixes"]["audio_preview"]
    object_key = f"{prefix}{album_slug}/{sort_order:03d}.mp3"

    try:
        resp = requests.get(cdn_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.content
        file_size = len(data)

        if file_size == 0:
            logger.warning("下载音频为空: %s", cdn_url)
            return None

        client = _get_client()
        client.put_object(
            bucket, object_key,
            io.BytesIO(data), file_size,
            content_type="audio/mpeg",
        )

        logger.info("音频已上传: %s (%d bytes)", object_key, file_size)
        return object_key, file_size

    except Exception:
        logger.warning("音频下载/上传失败: %s", cdn_url, exc_info=True)
        return None
