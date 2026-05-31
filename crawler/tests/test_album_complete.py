"""_album_is_complete 单元测试（适配新架构）。"""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from indietracks_spider.spiders.album_base import BaseAlbumSpider


class TestAlbumIsComplete:
    """测试 _album_is_complete 方法。"""

    def _make_spider(self):
        """创建一个 BaseAlbumSpider 实例用于测试。"""
        spider = BaseAlbumSpider.__new__(BaseAlbumSpider)
        spider._db_conn = None
        spider._db_cur = None
        return spider

    @patch('indietracks_spider.spiders.album_base.get_storage_backend')
    @patch.object(BaseAlbumSpider, '_ensure_db')
    def test_complete_album(self, mock_ensure_db, mock_storage):
        """info_title 非空 → 返回 True。"""
        spider = self._make_spider()
        spider.repo = MagicMock()
        spider.repo.is_album_complete.return_value = True

        result = spider._album_is_complete("SW20")

        assert result is True
        spider.repo.is_album_complete.assert_called_once_with("SW20")

    @patch('indietracks_spider.spiders.album_base.get_storage_backend')
    @patch.object(BaseAlbumSpider, '_ensure_db')
    def test_incomplete_album(self, mock_ensure_db, mock_storage):
        """info_title 为 NULL → 返回 False。"""
        spider = self._make_spider()
        spider.repo = MagicMock()
        spider.repo.is_album_complete.return_value = False

        result = spider._album_is_complete("SW20")

        assert result is False

    @patch('indietracks_spider.spiders.album_base.get_storage_backend')
    @patch.object(BaseAlbumSpider, '_ensure_db')
    def test_nonexistent_album(self, mock_ensure_db, mock_storage):
        """专辑不存在 → 返回 False。"""
        spider = self._make_spider()
        spider.repo = MagicMock()
        spider.repo.is_album_complete.return_value = False

        result = spider._album_is_complete("NONEXIST")

        assert result is False
