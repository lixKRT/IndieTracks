"""MinIO 音频下载 + 上传工具（向后兼容层）。

此模块现在代理到 storage.py 的 StorageBackend。
新代码应直接使用 storage.py。
"""

from __future__ import annotations

from indietracks_spider.utils.storage import (
    download_image,
    download_and_upload,
    get_storage_backend,
    set_storage_backend,
)

__all__ = ["download_image", "download_and_upload", "get_storage_backend", "set_storage_backend"]
