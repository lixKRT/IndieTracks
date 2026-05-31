"""DbSpiderMixin — 统一蜘蛛数据库连接管理。

消除 4 个蜘蛛中重复的 _ensure_db / _db_conn / _db_cur / close_connection 样板。

用法:
    class MySpider(DbSpiderMixin, scrapy.Spider):
        def parse(self, response):
            self.repo.is_album_complete("some-slug")
"""

from __future__ import annotations

from indietracks_spider.repository import Repository
from indietracks_spider.utils.db import DbConnection


class DbSpiderMixin:
    """为蜘蛛提供统一的数据库连接和 Repository 访问。

    混入此类后，蜘蛛可通过以下属性访问数据库：
    - self.db — DbConnection 实例
    - self.repo — Repository 实例（带缓存的读写层）

    生命周期：
    - _ensure_db() — 懒初始化连接（首次调用时建立）
    - closed() — 关闭连接（子类应调用 super().closed(reason)）
    """

    db: DbConnection
    repo: Repository

    def _ensure_db(self) -> None:
        """懒初始化数据库连接和 Repository。"""
        if hasattr(self, 'db') and self.db.connected:
            return
        if not hasattr(self, 'db'):
            self.db = DbConnection(autocommit=True)
        self.db.connect()
        if not hasattr(self, 'repo'):
            self.repo = Repository(self.db)

    def _close_db(self) -> None:
        """关闭数据库连接。"""
        if hasattr(self, 'db'):
            self.db.close()

    def closed(self, reason: str) -> None:
        """蜘蛛关闭时清理数据库连接。子类应调用 super().closed(reason)。"""
        self._close_db()
