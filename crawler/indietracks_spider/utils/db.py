"""共享数据库连接工具。

提供 DbConnection 上下文管理器，统一连接生命周期。
支持注入 config dict，便于测试。
"""

from __future__ import annotations

import logging
from typing import Any

import psycopg2
import psycopg2.extensions

logger = logging.getLogger(__name__)


class DbConnection:
    """数据库连接封装，支持上下文管理器和属性访问。

    用法:
        # 生产环境（从 config/database.json 读取）
        with DbConnection() as db:
            db.cursor.execute("SELECT 1")

        # 测试环境（注入 config dict）
        with DbConnection(config={"host":"localhost",...}) as db:
            ...
    """

    def __init__(self, autocommit: bool = True, config: dict | None = None):
        self._autocommit = autocommit
        self._config = config  # 注入 config，None 则从文件读取
        self._conn: psycopg2.extensions.connection | None = None
        self._cur: psycopg2.extensions.cursor | None = None

    @property
    def conn(self) -> psycopg2.extensions.connection:
        if self._conn is None:
            raise RuntimeError("数据库未连接，请先调用 connect() 或使用 with 语句")
        return self._conn

    @property
    def cursor(self) -> psycopg2.extensions.cursor:
        if self._cur is None:
            raise RuntimeError("数据库未连接，请先调用 connect() 或使用 with 语句")
        return self._cur

    @property
    def connected(self) -> bool:
        return self._cur is not None

    def connect(self) -> None:
        """建立数据库连接。"""
        if self._cur is not None:
            return
        if self._config:
            cfg = self._config
        else:
            from indietracks_spider.utils.config_loader import get_database_config
            cfg = get_database_config()
        if not cfg.get("user"):
            raise RuntimeError(
                "数据库用户名未配置。请编辑 crawler/config/database.json 填入 user 和 password"
            )
        self._conn = psycopg2.connect(
            host=cfg["host"],
            port=cfg["port"],
            database=cfg["database"],
            user=cfg["user"],
            password=cfg["password"],
            options="-c client_encoding=UTF8",
        )
        self._conn.autocommit = self._autocommit
        self._cur = self._conn.cursor()
        logger.info("数据库已连接: %s:%s/%s", cfg["host"], cfg["port"], cfg["database"])

    def close(self) -> None:
        """关闭游标和连接。"""
        if self._cur:
            self._cur.close()
            self._cur = None
        if self._conn:
            self._conn.close()
            self._conn = None

    def commit(self) -> None:
        """提交事务（仅非 autocommit 模式有效）。"""
        if self._conn and not self._autocommit:
            self._conn.commit()

    def rollback(self) -> None:
        """回滚事务。"""
        if self._conn:
            self._conn.rollback()

    def __enter__(self) -> DbConnection:
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


# ── 旧接口兼容 ─────────────────────────────────────────


def get_connection(autocommit: bool = True) -> tuple[Any, Any]:
    """获取 psycopg2 连接和游标（旧接口，保持向后兼容）。"""
    from indietracks_spider.utils.config_loader import get_database_config
    db_cfg = get_database_config()
    if not db_cfg.get("user"):
        raise RuntimeError("数据库未配置，请编辑 crawler/config/database.json")
    conn = psycopg2.connect(
        host=db_cfg["host"],
        port=db_cfg["port"],
        database=db_cfg["database"],
        user=db_cfg["user"],
        password=db_cfg["password"],
        options="-c client_encoding=UTF8",
    )
    if autocommit:
        conn.autocommit = True
    return conn, conn.cursor()


def close_connection(conn, cur):
    """安全关闭游标和连接（旧接口，保持向后兼容）。"""
    if cur:
        cur.close()
    if conn:
        conn.close()
