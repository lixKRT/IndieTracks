"""storage.py 单元测试。"""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from indietracks_spider.utils.storage import (
    StorageBackend,
    MinioBackend,
    MemoryBackend,
    set_storage_backend,
    download_image,
    download_and_upload,
)


class TestStorageBackendStatic:
    """测试 StorageBackend 的静态方法。"""

    def test_detect_image_prefix_cover(self):
        assert StorageBackend.detect_image_prefix("https://cdn.dizzylab.net/media/cover/abc.jpg") == "covers"

    def test_detect_image_prefix_label_cover(self):
        assert StorageBackend.detect_image_prefix("https://cdn.dizzylab.net/media/label_cover/abc.jpg") == "logos"

    def test_detect_image_prefix_avatars(self):
        assert StorageBackend.detect_image_prefix("https://cdn.dizzylab.net/media/avatars/abc.jpg") == "avatars"

    def test_detect_image_prefix_unknown(self):
        assert StorageBackend.detect_image_prefix("https://cdn.dizzylab.net/media/other/abc.jpg") is None

    def test_detect_image_prefix_empty(self):
        assert StorageBackend.detect_image_prefix("") is None

    def test_extract_filename_strips_cdn_suffix(self):
        # CDN 变换后缀 !cover 被去掉，保留原始文件名部分
        assert StorageBackend.extract_filename("https://cdn.dizzylab.net/media/cover/abc!cover.jpg") == "abc"

    def test_extract_filename_no_suffix(self):
        assert StorageBackend.extract_filename("https://cdn.dizzylab.net/media/cover/abc.jpg") == "abc.jpg"

    def test_extract_filename_avatar_little(self):
        assert StorageBackend.extract_filename("https://cdn.dizzylab.net/media/avatars/user123!avatarlittle.jpg") == "user123"


class TestMemoryBackend:
    """测试 MemoryBackend。"""

    def test_upload_image_cover(self):
        backend = MemoryBackend()
        result = backend.upload_image("https://cdn.dizzylab.net/media/cover/abc.jpg")
        assert result is not None
        assert "covers" in result
        assert result in backend.images

    def test_upload_image_avatar(self):
        backend = MemoryBackend()
        result = backend.upload_image("https://cdn.dizzylab.net/media/avatars/user.jpg")
        assert result is not None
        assert "avatars" in result

    def test_upload_image_empty_url(self):
        backend = MemoryBackend()
        assert backend.upload_image("") is None

    def test_upload_image_non_cdn(self):
        backend = MemoryBackend()
        assert backend.upload_image("https://example.com/other/image.jpg") is None

    def test_upload_audio(self):
        backend = MemoryBackend()
        result = backend.upload_audio("https://cdn.dizzylab.net/audio/track.mp3", "album-slug", 1)
        assert result is not None
        object_key, file_size = result
        assert "album-slug" in object_key
        assert "001.mp3" in object_key
        assert file_size > 0
        assert object_key in backend.audios

    def test_upload_audio_empty_url(self):
        backend = MemoryBackend()
        assert backend.upload_audio("", "slug", 1) is None

    def test_counter_increments(self):
        backend = MemoryBackend()
        backend.upload_image("https://cdn.dizzylab.net/media/cover/a.jpg")
        backend.upload_image("https://cdn.dizzylab.net/media/cover/b.jpg")
        assert backend._image_counter == 2

    def test_audio_sort_order_format(self):
        backend = MemoryBackend()
        result = backend.upload_audio("https://cdn.dizzylab.net/audio/t.mp3", "slug", 5)
        assert result is not None
        assert "005.mp3" in result[0]


class TestGlobalBackend:
    """测试全局存储后端注入。"""

    def test_set_and_use_backend(self):
        backend = MemoryBackend()
        set_storage_backend(backend)
        result = download_image("https://cdn.dizzylab.net/media/cover/test.jpg")
        assert result is not None

    def test_download_and_upload_proxy(self):
        backend = MemoryBackend()
        set_storage_backend(backend)
        result = download_and_upload("https://cdn.dizzylab.net/audio/t.mp3", "slug", 1)
        assert result is not None
        assert len(result) == 2

    def teardown_method(self):
        """重置全局后端。"""
        import indietracks_spider.utils.storage as mod
        mod._backend = None
