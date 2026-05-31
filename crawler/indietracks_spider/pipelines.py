"""
PostgreSQL 写入 Pipeline（重构版）。

使用 ItemRegistry 调度 + Repository 统一持久化。
新增 Item 只需在 items.py 定义 + item_registry.register()，不碰此文件。
"""

import logging
from collections import Counter

from indietracks_spider.item_registry import get_handler
from indietracks_spider.repository import Repository
from indietracks_spider.utils.db import DbConnection

logger = logging.getLogger(__name__)


class PostgresPipeline:
    def open_spider(self, spider):
        self._db = DbConnection(autocommit=False)
        self._db.connect()
        self._repo = Repository(self._db)
        self._counts = Counter()  # 按 Item 类型统计
        spider.logger.info("Pipeline 数据库已连接")

    def close_spider(self, spider):
        self._db.commit()
        self._db.close()
        # 打印汇总
        if self._counts:
            parts = [f"{name}={cnt}" for name, cnt in self._counts.most_common()]
            spider.logger.info("Pipeline 写入汇总: %s", " | ".join(parts))
        spider.logger.info("Pipeline 数据库连接已关闭")

    def process_item(self, item, spider):
        try:
            # 查找注册表中的处理函数
            handler = get_handler(type(item))
            if handler is None:
                spider.logger.warning("未注册的 Item 类型: %s", type(item).__name__)
                return item

            resolve_fn, upsert_fn = handler

            # 阶段 0：解析临时关联字段（_ 前缀）为实际 ID
            resolve_fn(item, self._repo)

            # 阶段 1：写入数据库
            upsert_fn(item, self._repo)

            self._db.commit()
            self._counts[type(item).__name__] += 1
        except Exception:
            self._db.rollback()
            spider.logger.error("写入失败，已回滚: %s", item, exc_info=True)
            return None
        return item
