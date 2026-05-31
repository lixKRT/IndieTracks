"""utils/db.py 单元测试。"""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from indietracks_spider.utils.db import DbConnection, get_connection, close_connection


TEST_CONFIG = {
    "host": "localhost", "port": 5432,
    "database": "testdb", "user": "user", "password": "pass",
}


# ── DbConnection ──────────────────────────────────────


class TestDbConnection:
    def test_initial_state(self):
        db = DbConnection()
        assert db.connected is False
        assert db._conn is None
        assert db._cur is None

    def test_property_conn_raises_before_connect(self):
        db = DbConnection()
        with pytest.raises(RuntimeError, match="数据库未连接"):
            _ = db.conn

    def test_property_cursor_raises_before_connect(self):
        db = DbConnection()
        with pytest.raises(RuntimeError, match="数据库未连接"):
            _ = db.cursor

    @patch("indietracks_spider.utils.db.psycopg2")
    def test_connect(self, mock_pg):
        mock_conn = MagicMock()
        mock_pg.connect.return_value = mock_conn

        db = DbConnection(autocommit=True, config=TEST_CONFIG)
        db.connect()

        assert db.connected is True
        mock_pg.connect.assert_called_once()
        assert mock_conn.autocommit is True

    @patch("indietracks_spider.utils.db.psycopg2")
    def test_connect_idempotent(self, mock_pg):
        mock_pg.connect.return_value = MagicMock()

        db = DbConnection(config=TEST_CONFIG)
        db.connect()
        db.connect()  # 第二次不应重新连接
        assert mock_pg.connect.call_count == 1

    @patch("indietracks_spider.utils.db.psycopg2")
    def test_close(self, mock_pg):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_pg.connect.return_value = mock_conn

        db = DbConnection(config=TEST_CONFIG)
        db.connect()
        db.close()

        assert db.connected is False
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_close_noop_when_not_connected(self):
        db = DbConnection()
        db.close()  # 不应抛异常

    @patch("indietracks_spider.utils.db.psycopg2")
    def test_context_manager(self, mock_pg):
        mock_conn = MagicMock()
        mock_pg.connect.return_value = mock_conn

        with DbConnection(config=TEST_CONFIG) as db:
            assert db.connected is True

        assert db.connected is False

    @patch("indietracks_spider.utils.db.psycopg2")
    def test_commit_autocommit_off(self, mock_pg):
        mock_conn = MagicMock()
        mock_pg.connect.return_value = mock_conn

        db = DbConnection(autocommit=False, config=TEST_CONFIG)
        db.connect()
        db.commit()
        mock_conn.commit.assert_called_once()

    @patch("indietracks_spider.utils.db.psycopg2")
    def test_commit_autocommit_on_skips(self, mock_pg):
        mock_conn = MagicMock()
        mock_pg.connect.return_value = mock_conn

        db = DbConnection(autocommit=True, config=TEST_CONFIG)
        db.connect()
        db.commit()
        mock_conn.commit.assert_not_called()

    @patch("indietracks_spider.utils.db.psycopg2")
    def test_rollback(self, mock_pg):
        mock_conn = MagicMock()
        mock_pg.connect.return_value = mock_conn

        db = DbConnection(config=TEST_CONFIG)
        db.connect()
        db.rollback()
        mock_conn.rollback.assert_called_once()

    def test_rollback_noop_when_not_connected(self):
        db = DbConnection()
        db.rollback()  # 不应抛异常

    def test_missing_user_raises(self):
        cfg = {"host": "localhost", "port": 5432, "database": "db", "user": "", "password": ""}
        db = DbConnection(config=cfg)
        with pytest.raises(RuntimeError, match="数据库用户名未配置"):
            db.connect()

    @patch("indietracks_spider.utils.db.psycopg2")
    def test_injected_config(self, mock_pg):
        """测试注入 config dict，不需要真实配置文件。"""
        mock_pg.connect.return_value = MagicMock()
        db = DbConnection(config=TEST_CONFIG)
        db.connect()
        mock_pg.connect.assert_called_once()
        assert db.connected is True
        db.close()

    def test_injected_config_missing_user(self):
        cfg = {"host": "localhost", "port": 5432, "database": "db", "user": "", "password": ""}
        db = DbConnection(config=cfg)
        with pytest.raises(RuntimeError, match="数据库用户名未配置"):
            db.connect()


# ── 旧接口兼容 ─────────────────────────────────────────


class TestGetConnection:
    @patch('indietracks_spider.utils.config_loader.get_database_config')
    @patch('indietracks_spider.utils.db.psycopg2')
    def test_returns_tuple(self, mock_psycopg2, mock_get_config):
        mock_get_config.return_value = {
            'host': 'localhost', 'port': 5432,
            'database': 'test', 'user': 'test', 'password': 'test'
        }
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        conn, cur = get_connection()

        assert conn == mock_conn
        assert cur == mock_cursor
        mock_psycopg2.connect.assert_called_once()

    @patch('indietracks_spider.utils.config_loader.get_database_config')
    def test_raises_on_missing_user(self, mock_get_config):
        mock_get_config.return_value = {'user': '', 'password': ''}
        with pytest.raises(RuntimeError, match="数据库未配置"):
            get_connection()


class TestCloseConnection:
    def test_closes_both(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        close_connection(mock_conn, mock_cur)
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_handles_none(self):
        close_connection(None, None)  # Should not raise
