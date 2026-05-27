"""共享数据库连接工具。"""

from typing import Any

import psycopg2

from indietracks_spider.utils.config_loader import get_database_config


def get_connection(autocommit: bool = True) -> tuple[Any, Any, Any]:
    """获取 psycopg2 连接和游标。

    Returns (conn, cur) 元组。
    """
    db = get_database_config()
    if not db.get("user"):
        raise RuntimeError("数据库未配置，请编辑 crawler/config/database.json")
    conn = psycopg2.connect(
        host=db["host"],
        port=db["port"],
        database=db["database"],
        user=db["user"],
        password=db["password"],
        options="-c client_encoding=UTF8",
    )
    if autocommit:
        conn.autocommit = True
    return conn, conn.cursor()


def close_connection(conn, cur):
    """安全关闭游标和连接。"""
    if cur:
        cur.close()
    if conn:
        conn.close()
