"""测试基础设施 — 共享 fixtures。"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# 确保 crawler/ 在路径中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(autouse=True)
def _clear_config_overrides():
    """每个测试前清除配置覆盖。"""
    from indietracks_spider.utils.config_loader import clear_config_overrides
    clear_config_overrides()
    yield
    clear_config_overrides()


@pytest.fixture
def mock_db():
    """模拟 DbConnection，不连接真实数据库。"""
    from indietracks_spider.utils.db import DbConnection

    db = MagicMock(spec=DbConnection)
    db.connected = True
    db.cursor = MagicMock()
    db.conn = MagicMock()
    return db


@pytest.fixture
def mock_repo(mock_db):
    """模拟 Repository。"""
    from indietracks_spider.repository import Repository

    repo = MagicMock(spec=Repository)
    repo.cursor = mock_db.cursor
    return repo


@pytest.fixture
def memory_storage():
    """内存存储后端（测试用）。"""
    from indietracks_spider.utils.storage import MemoryBackend
    return MemoryBackend()


@pytest.fixture
def make_response():
    """创建模拟 Scrapy Response 的工厂函数。"""
    from scrapy.http import TextResponse

    def _make(url="https://example.com", body=b"", meta=None, status=200):
        return TextResponse(
            url=url,
            body=body,
            encoding="utf-8",
            meta=meta or {},
        )
    return _make


@pytest.fixture
def make_html_response():
    """创建 HTML Response 的工厂函数。"""
    from scrapy.http import TextResponse

    def _make(url="https://example.com", html="", meta=None, status=200):
        return TextResponse(
            url=url,
            body=html.encode("utf-8"),
            encoding="utf-8",
            meta=meta or {},
        )
    return _make


@pytest.fixture
def make_json_response():
    """创建 JSON Response 的工厂函数。"""
    import json
    from scrapy.http import TextResponse

    def _make(url="https://example.com", data=None, meta=None, status=200):
        body = json.dumps(data or {}).encode("utf-8")
        return TextResponse(
            url=url,
            body=body,
            encoding="utf-8",
            meta=meta or {},
        )
    return _make
