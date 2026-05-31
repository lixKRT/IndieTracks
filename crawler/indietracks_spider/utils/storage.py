"""存储后端抽象 — 可替换的文件存储接口。

提供 StorageBackend 抽象接口，生产环境用 MinioBackend，
测试用 MemoryBackend。
"""

from __future__ import annotations

import io
import logging
from abc import ABC, abstractmethod
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
}

# CDN URL 路径 → minio.json prefixes 映射
_IMAGE_PREFIX_MAP = {
    "/media/cover/": "covers",
    "/media/label_cover/": "logos",
    "/media/avatars/": "avatars",
}


class StorageBackend(ABC):
    """存储后端抽象接口。"""

    @abstractmethod
    def upload_image(self, cdn_url: str) -> str | None:
        """下载图片 → 上传存储 → 返回 object_key。

        非图片 CDN URL 或下载失败返回 None。
        """
        ...

    @abstractmethod
    def upload_audio(self, cdn_url: str, album_slug: str, sort_order: int) -> tuple[str, int] | None:
        """下载试听音频 → 上传存储。

        Returns (object_key, file_size) 或 None（失败时跳过）。
        """
        ...

    @staticmethod
    def detect_image_prefix(cdn_url: str) -> str | None:
        """根据 CDN URL 路径判断图片前缀 key（covers/logos/avatars）。"""
        for path_pattern, key in _IMAGE_PREFIX_MAP.items():
            if path_pattern in cdn_url:
                return key
        return None

    @staticmethod
    def extract_filename(cdn_url: str) -> str:
        """从 URL 提取文件名：去掉 !cover / !avatarlittle 等后缀。"""
        url_path = urlparse(cdn_url).path
        return url_path.split("/")[-1].split("!")[0]


class MinioBackend(StorageBackend):
    """MinIO 存储后端（生产环境）。"""

    def __init__(self, config: dict):
        """
        Args:
            config: minio.json 内容，含 endpoint/access_key/secret_key/bucket/prefixes
        """
        from minio import Minio

        self._cfg = config
        endpoint = config["endpoint"].replace("http://", "").replace("https://", "")
        self._client = Minio(
            endpoint,
            access_key=config["access_key"],
            secret_key=config["secret_key"],
            secure=False,
        )

    def upload_image(self, cdn_url: str) -> str | None:
        if not cdn_url:
            return None

        prefix_key = self.detect_image_prefix(cdn_url)
        if prefix_key is None:
            logger.debug("非图片 CDN URL，跳过: %s", cdn_url)
            return None

        bucket = self._cfg["bucket"]
        prefix = self._cfg["prefixes"][prefix_key]
        filename = self.extract_filename(cdn_url)
        object_key = f"{prefix}{filename}"

        try:
            resp = requests.get(cdn_url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.content
            file_size = len(data)

            if file_size == 0:
                logger.warning("下载图片为空: %s", cdn_url)
                return None

            self._client.put_object(
                bucket, object_key,
                io.BytesIO(data), file_size,
            )
            logger.info("图片已上传: %s (%d bytes)", object_key, file_size)
            return object_key

        except Exception:
            logger.warning("图片下载/上传失败: %s", cdn_url, exc_info=True)
            return None

    def upload_audio(self, cdn_url: str, album_slug: str, sort_order: int) -> tuple[str, int] | None:
        bucket = self._cfg["bucket"]
        prefix = self._cfg["prefixes"]["audio_preview"]
        object_key = f"{prefix}{album_slug}/{sort_order:03d}.mp3"

        try:
            resp = requests.get(cdn_url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.content
            file_size = len(data)

            if file_size == 0:
                logger.warning("下载音频为空: %s", cdn_url)
                return None

            self._client.put_object(
                bucket, object_key,
                io.BytesIO(data), file_size,
                content_type="audio/mpeg",
            )
            logger.info("音频已上传: %s (%d bytes)", object_key, file_size)
            return object_key, file_size

        except Exception:
            logger.warning("音频下载/上传失败: %s", cdn_url, exc_info=True)
            return None


class MemoryBackend(StorageBackend):
    """内存存储后端（测试用，不发起真实 HTTP 请求）。"""

    def __init__(self):
        self.images: dict[str, bytes] = {}      # object_key → data
        self.audios: dict[str, bytes] = {}       # object_key → data
        self._image_counter = 0
        self._audio_counter = 0

    def upload_image(self, cdn_url: str) -> str | None:
        if not cdn_url:
            return None
        prefix_key = self.detect_image_prefix(cdn_url)
        if prefix_key is None:
            return None
        self._image_counter += 1
        object_key = f"test/{prefix_key}/{self._image_counter}.jpg"
        self.images[object_key] = b"fake-image-data"
        return object_key

    def upload_audio(self, cdn_url: str, album_slug: str, sort_order: int) -> tuple[str, int] | None:
        if not cdn_url:
            return None
        self._audio_counter += 1
        object_key = f"test/audio/preview/{album_slug}/{sort_order:03d}.mp3"
        data = b"fake-audio-data"
        self.audios[object_key] = data
        return object_key, len(data)


# ── 全局实例（向后兼容旧的函数式 API）─────────────────────

_backend: StorageBackend | None = None


def get_storage_backend() -> StorageBackend:
    """获取全局存储后端实例（懒初始化）。"""
    global _backend
    if _backend is None:
        from indietracks_spider.utils.config_loader import get_minio_config
        _backend = MinioBackend(get_minio_config())
    return _backend


def set_storage_backend(backend: StorageBackend) -> None:
    """注入存储后端（测试用）。"""
    global _backend
    _backend = backend


def download_image(cdn_url: str) -> str | None:
    """下载图片 → 上传 MinIO → 返回 object_key（兼容旧 API）。"""
    return get_storage_backend().upload_image(cdn_url)


def download_and_upload(cdn_url: str, album_slug: str, sort_order: int) -> tuple[str, int] | None:
    """下载试听音频 → 上传 MinIO（兼容旧 API）。"""
    return get_storage_backend().upload_audio(cdn_url, album_slug, sort_order)
