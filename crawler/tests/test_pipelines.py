"""pipelines.py 单元测试。"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from indietracks_spider.pipelines import PostgresPipeline
from indietracks_spider.items import TagItem, AlbumItem, CircleItem


class TestPostgresPipeline:
    @patch("indietracks_spider.pipelines.DbConnection")
    @patch("indietracks_spider.pipelines.Repository")
    def test_open_spider_creates_connection(self, mock_repo_cls, mock_db_cls):
        mock_db = MagicMock()
        mock_db_cls.return_value = mock_db

        pipeline = PostgresPipeline()
        spider = MagicMock()
        pipeline.open_spider(spider)

        mock_db.connect.assert_called_once()
        mock_repo_cls.assert_called_once_with(mock_db)

    @patch("indietracks_spider.pipelines.DbConnection")
    @patch("indietracks_spider.pipelines.Repository")
    def test_close_spider_commits_and_closes(self, mock_repo_cls, mock_db_cls):
        mock_db = MagicMock()
        mock_db_cls.return_value = mock_db

        pipeline = PostgresPipeline()
        spider = MagicMock()
        pipeline.open_spider(spider)
        pipeline.close_spider(spider)

        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("indietracks_spider.pipelines.DbConnection")
    @patch("indietracks_spider.pipelines.Repository")
    def test_close_spider_logs_counts(self, mock_repo_cls, mock_db_cls):
        mock_db = MagicMock()
        mock_db_cls.return_value = mock_db

        pipeline = PostgresPipeline()
        spider = MagicMock()
        pipeline.open_spider(spider)
        pipeline._counts["TagItem"] = 10
        pipeline._counts["AlbumItem"] = 3
        pipeline.close_spider(spider)

        # 验证汇总日志被调用
        spider.logger.info.assert_any_call(
            "Pipeline 写入汇总: %s",
            "TagItem=10 | AlbumItem=3",
        )

    @patch("indietracks_spider.pipelines.DbConnection")
    @patch("indietracks_spider.pipelines.Repository")
    @patch("indietracks_spider.pipelines.get_handler")
    def test_process_item_calls_handler(self, mock_get_handler, mock_repo_cls, mock_db_cls):
        mock_db = MagicMock()
        mock_db_cls.return_value = mock_db

        resolve_fn = MagicMock()
        upsert_fn = MagicMock()
        mock_get_handler.return_value = (resolve_fn, upsert_fn)

        pipeline = PostgresPipeline()
        pipeline.open_spider(MagicMock())

        item = TagItem()
        item["name"] = "test"
        result = pipeline.process_item(item, MagicMock())

        resolve_fn.assert_called_once()
        upsert_fn.assert_called_once()
        mock_db.commit.assert_called()
        assert result is item

    @patch("indietracks_spider.pipelines.DbConnection")
    @patch("indietracks_spider.pipelines.Repository")
    @patch("indietracks_spider.pipelines.get_handler")
    def test_process_item_unknown_type(self, mock_get_handler, mock_repo_cls, mock_db_cls):
        mock_db = MagicMock()
        mock_db_cls.return_value = mock_db
        mock_get_handler.return_value = None

        pipeline = PostgresPipeline()
        pipeline.open_spider(MagicMock())

        item = {"unknown": "data"}
        result = pipeline.process_item(item, MagicMock())
        assert result is item  # 返回原 item，不崩溃

    @patch("indietracks_spider.pipelines.DbConnection")
    @patch("indietracks_spider.pipelines.Repository")
    @patch("indietracks_spider.pipelines.get_handler")
    def test_process_item_rollback_on_error(self, mock_get_handler, mock_repo_cls, mock_db_cls):
        mock_db = MagicMock()
        mock_db_cls.return_value = mock_db

        resolve_fn = MagicMock(side_effect=Exception("DB error"))
        upsert_fn = MagicMock()
        mock_get_handler.return_value = (resolve_fn, upsert_fn)

        pipeline = PostgresPipeline()
        pipeline.open_spider(MagicMock())

        item = TagItem()
        result = pipeline.process_item(item, MagicMock())

        mock_db.rollback.assert_called_once()
        assert result is None
