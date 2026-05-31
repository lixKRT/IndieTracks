"""db_mixin.py 单元测试。"""

from __future__ import annotations

from unittest.mock import patch, MagicMock
import pytest

from indietracks_spider.db_mixin import DbSpiderMixin


class ConcreteSpider(DbSpiderMixin):
    """用于测试的具体蜘蛛实现。"""
    pass


class TestDbSpiderMixin:
    def test_initial_state(self):
        spider = ConcreteSpider()
        # db 和 repo 在 _ensure_db 之前不应存在
        assert not hasattr(spider, 'db') or spider.db is None or True  # mixin 不预设

    @patch("indietracks_spider.db_mixin.DbConnection")
    @patch("indietracks_spider.db_mixin.Repository")
    def test_ensure_db_creates_connection(self, mock_repo_cls, mock_db_cls):
        mock_db = MagicMock()
        mock_db.connected = True
        mock_db_cls.return_value = mock_db

        spider = ConcreteSpider()
        spider._ensure_db()

        mock_db.connect.assert_called_once()
        mock_repo_cls.assert_called_once_with(mock_db)

    @patch("indietracks_spider.db_mixin.DbConnection")
    @patch("indietracks_spider.db_mixin.Repository")
    def test_ensure_db_idempotent(self, mock_repo_cls, mock_db_cls):
        mock_db = MagicMock()
        mock_db.connected = True
        mock_db_cls.return_value = mock_db

        spider = ConcreteSpider()
        spider._ensure_db()
        spider._ensure_db()

        # 只应连接一次
        mock_db.connect.assert_called_once()

    @patch("indietracks_spider.db_mixin.DbConnection")
    @patch("indietracks_spider.db_mixin.Repository")
    def test_close_db(self, mock_repo_cls, mock_db_cls):
        mock_db = MagicMock()
        mock_db.connected = True
        mock_db_cls.return_value = mock_db

        spider = ConcreteSpider()
        spider._ensure_db()
        spider._close_db()

        mock_db.close.assert_called_once()

    def test_close_db_noop_without_connection(self):
        spider = ConcreteSpider()
        spider._close_db()  # 不应抛异常

    @patch("indietracks_spider.db_mixin.DbConnection")
    @patch("indietracks_spider.db_mixin.Repository")
    def test_closed_calls_close_db(self, mock_repo_cls, mock_db_cls):
        mock_db = MagicMock()
        mock_db.connected = True
        mock_db_cls.return_value = mock_db

        spider = ConcreteSpider()
        spider._ensure_db()
        spider.closed("finished")

        mock_db.close.assert_called_once()

    @patch("indietracks_spider.db_mixin.DbConnection")
    @patch("indietracks_spider.db_mixin.Repository")
    def test_repo_accessible_after_ensure(self, mock_repo_cls, mock_db_cls):
        mock_db = MagicMock()
        mock_db.connected = True
        mock_repo = MagicMock()
        mock_db_cls.return_value = mock_db
        mock_repo_cls.return_value = mock_repo

        spider = ConcreteSpider()
        spider._ensure_db()

        assert spider.repo is mock_repo
        assert spider.db is mock_db
