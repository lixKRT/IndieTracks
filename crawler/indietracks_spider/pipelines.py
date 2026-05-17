"""
PostgreSQL 写入 Pipeline。

去重策略：
- albums / circles / users / tags：各自 UNIQUE 列检测冲突
- work_files：先 DELETE 旧数据再 INSERT（以专辑为单位刷新）
- 关联表：ON CONFLICT DO NOTHING

维护内存映射：dizzylab_id → db_id，避免跨 Item 重复查询。
"""

import json
import logging
from datetime import datetime

import psycopg2

from indietracks_spider.items import (
    AlbumItem, WorkFileItem, CircleItem, AlbumCircleItem,
    TagItem, AlbumTagItem, UserItem, UserCircleItem,
    CommentItem, OwnedAlbumItem,
)
from indietracks_spider.utils.config_loader import get_database_config

logger = logging.getLogger(__name__)


class PostgresPipeline:
    def open_spider(self, spider):
        db = get_database_config()
        if not db.get("user"):
            raise RuntimeError(
                "数据库用户名未配置。请编辑 crawler/config/database.json 填入 user 和 password"
            )

        self.conn = psycopg2.connect(
            host=db["host"],
            port=db["port"],
            database=db["database"],
            user=db["user"],
            password=db["password"],
            options="-c client_encoding=UTF8",
        )
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()
        spider.logger.info("数据库已连接: %s:%s/%s", db["host"], db["port"], db["database"])

        # 内存映射缓存：避免对同一 dizzylab_id 反复 SELECT
        self._album_id_cache: dict[str, int] = {}       # dizzylab_id → album_id
        self._circle_id_cache: dict[int, int] = {}       # dizzylab_labelid → circle_id
        self._user_id_cache: dict[int, int] = {}         # dizzylab_user_id → user_id
        self._tag_id_cache: dict[str, int] = {}          # tag_name → tag_id

        # 已插入 work_files 的 album_id，用于清旧数据
        self._workfile_flushed: set[int] = set()

    def close_spider(self, spider):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        spider.logger.info("数据库连接已关闭")

    def process_item(self, item, spider):
        try:
            # 阶段 0：解析临时关联字段（_ 前缀）为实际 ID
            self._resolve_refs(item)

            if isinstance(item, TagItem):
                self._upsert_tag(item)
            elif isinstance(item, CircleItem):
                self._upsert_circle(item)
            elif isinstance(item, UserItem):
                self._upsert_user(item)
            elif isinstance(item, AlbumItem):
                self._upsert_album(item)
            elif isinstance(item, WorkFileItem):
                self._upsert_workfile(item)
            elif isinstance(item, AlbumCircleItem):
                self._upsert_album_circle(item)
            elif isinstance(item, AlbumTagItem):
                self._upsert_album_tag(item)
            elif isinstance(item, UserCircleItem):
                self._upsert_user_circle(item)
            elif isinstance(item, CommentItem):
                self._upsert_comment(item)
            elif isinstance(item, OwnedAlbumItem):
                self._upsert_owned(item)

            self.conn.commit()
        except Exception:
            self.conn.rollback()
            spider.logger.error("写入失败，已回滚: %s", item, exc_info=True)
        return item

    # ── 临时关联字段解析 ─────────────────────────────

    def _resolve_refs(self, item):
        """将 Spider 中暂存的 _dizzylab_id / _tag_name 等临时字段
        替换为实际的数据库主键。"""
        # AlbumTagItem: _tag_name → tag_id, _dizzylab_id → album_id
        if isinstance(item, AlbumTagItem):
            if not item.get("album_id") and item.get("_dizzylab_id"):
                item["album_id"] = self._album_id_cache.get(item["_dizzylab_id"])
            if not item.get("tag_id") and item.get("_tag_name"):
                item["tag_id"] = self._tag_id_cache.get(item["_tag_name"])

        # AlbumCircleItem: _dizzylab_labelid → circle_id, _dizzylab_id → album_id
        elif isinstance(item, AlbumCircleItem):
            if not item.get("album_id") and item.get("_dizzylab_id"):
                item["album_id"] = self._album_id_cache.get(item["_dizzylab_id"])
            if not item.get("circle_id") and item.get("_dizzylab_labelid"):
                item["circle_id"] = self._circle_id_cache.get(item["_dizzylab_labelid"])

        # OwnedAlbumItem: _dizzylab_user_id → user_id, _dizzylab_id → album_id
        elif isinstance(item, OwnedAlbumItem):
            if not item.get("user_id") and item.get("_dizzylab_user_id"):
                item["user_id"] = self._user_id_cache.get(item["_dizzylab_user_id"])
            if not item.get("album_id") and item.get("_dizzylab_id"):
                item["album_id"] = self._album_id_cache.get(item["_dizzylab_id"])

        # CommentItem: _dizzylab_user_id → user_id, _dizzylab_id → album_id
        elif isinstance(item, CommentItem):
            if not item.get("user_id") and item.get("_dizzylab_user_id"):
                item["user_id"] = self._user_id_cache.get(item["_dizzylab_user_id"])
            if not item.get("album_id") and item.get("_dizzylab_id"):
                item["album_id"] = self._album_id_cache.get(item["_dizzylab_id"])

        # UserCircleItem: _dizzylab_user_id → user_id, _dizzylab_labelid → circle_id
        elif isinstance(item, UserCircleItem):
            if not item.get("user_id") and item.get("_dizzylab_user_id"):
                item["user_id"] = self._user_id_cache.get(item["_dizzylab_user_id"])
            if not item.get("circle_id") and item.get("_dizzylab_labelid"):
                item["circle_id"] = self._circle_id_cache.get(item["_dizzylab_labelid"])

        # WorkFileItem: 需要 album_id（从 _dizzylab_id 或其他方式）
        # Spider 中 WorkFileItem 紧跟 AlbumItem yield，但 album_id 还不存在
        # 解决方案：在 yield AlbumItem 后，WorkFileItem 延迟到 _upsert_workfile 时
        # 通过 item 上暂时不设 album_id，由后续请求的 meta 传递
        # 当前 WorkFileItem 的 album_id 在 parse_album_detail 中设为 None
        # 需要改为通过 parse_album_detail 中的 album 缓存来设置
        elif isinstance(item, WorkFileItem):
            if not item.get("album_id") and item.get("_dizzylab_id"):
                item["album_id"] = self._album_id_cache.get(item["_dizzylab_id"])

    # ── 各表 upsert ────────────────────────────────────

    def _upsert_tag(self, item: TagItem):
        name = item["name"]
        if not name:
            return
        if name in self._tag_id_cache:
            item["tag_id"] = self._tag_id_cache[name]
            return
        self.cursor.execute(
            """INSERT INTO tags (name) VALUES (%s)
               ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name
               RETURNING tag_id""",
            (name,),
        )
        row = self.cursor.fetchone()
        if row:
            item["tag_id"] = row[0]
            self._tag_id_cache[name] = row[0]

    def _upsert_circle(self, item: CircleItem):
        lid = item.get("dizzylab_labelid")
        if lid in self._circle_id_cache:
            item["circle_id"] = self._circle_id_cache[lid]
            return
        self.cursor.execute(
            """INSERT INTO circles (dizzylab_labelid, name, description, logo_url)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (dizzylab_labelid) DO UPDATE
                 SET name=EXCLUDED.name,
                     logo_url=COALESCE(EXCLUDED.logo_url, circles.logo_url)
               RETURNING circle_id""",
            (lid, item.get("name"), item.get("description"), item.get("logo_url")),
        )
        row = self.cursor.fetchone()
        if row:
            item["circle_id"] = row[0]
            self._circle_id_cache[lid] = row[0]

    def _upsert_user(self, item: UserItem):
        uid = item.get("dizzylab_user_id")
        if not uid:
            return
        if uid in self._user_id_cache:
            item["user_id"] = self._user_id_cache[uid]
            return
        self.cursor.execute(
            """INSERT INTO users (dizzylab_user_id, username, avatar_url, user_role)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (dizzylab_user_id) DO UPDATE
                 SET username=EXCLUDED.username,
                     avatar_url=COALESCE(EXCLUDED.avatar_url, users.avatar_url)
               RETURNING user_id""",
            (uid, item.get("username"), item.get("avatar_url"), item.get("user_role", "normal")),
        )
        row = self.cursor.fetchone()
        if row:
            item["user_id"] = row[0]
            self._user_id_cache[uid] = row[0]

    def _upsert_album(self, item: AlbumItem):
        did = item["dizzylab_id"]
        if did in self._album_id_cache:
            item["album_id"] = self._album_id_cache[did]
            return
        self.cursor.execute(
            """INSERT INTO albums (dizzylab_id, title, info_title, info_content, price, cover_url, publish_date)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (dizzylab_id) DO UPDATE
                 SET title=EXCLUDED.title,
                     price=EXCLUDED.price,
                     cover_url=COALESCE(EXCLUDED.cover_url, albums.cover_url)
               RETURNING album_id""",
            (
                did,
                item.get("title"),
                item.get("info_title"),
                item.get("info_content"),
                item.get("price"),
                item.get("cover_url"),
                item.get("publish_date"),
            ),
        )
        row = self.cursor.fetchone()
        if row:
            item["album_id"] = row[0]
            self._album_id_cache[did] = row[0]

    def _upsert_workfile(self, item: WorkFileItem):
        """先删旧曲目，再插入新曲目（同一专辑刷新）。"""
        aid = item.get("album_id")
        if not aid:
            return
        # 每张专辑只清一次旧数据
        if aid not in self._workfile_flushed:
            self.cursor.execute("DELETE FROM work_files WHERE album_id = %s", (aid,))
            self._workfile_flushed.add(aid)

        self.cursor.execute(
            """INSERT INTO work_files (album_id, file_name, object_key, file_type, track_length, file_size, sort_order)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               RETURNING file_id""",
            (
                aid,
                item.get("file_name"),
                item.get("object_key"),
                item.get("file_type", "preview"),
                item.get("track_length"),
                item.get("file_size", 0),
                item.get("sort_order", 1),
            ),
        )
        row = self.cursor.fetchone()
        if row:
            item["file_id"] = row[0]

    def _upsert_album_circle(self, item: AlbumCircleItem):
        self.cursor.execute(
            """INSERT INTO album_circles (album_id, circle_id) VALUES (%s, %s)
               ON CONFLICT DO NOTHING""",
            (item["album_id"], item["circle_id"]),
        )

    def _upsert_album_tag(self, item: AlbumTagItem):
        self.cursor.execute(
            """INSERT INTO album_tags (album_id, tag_id) VALUES (%s, %s)
               ON CONFLICT DO NOTHING""",
            (item["album_id"], item["tag_id"]),
        )

    def _upsert_user_circle(self, item: UserCircleItem):
        self.cursor.execute(
            """INSERT INTO user_circles (user_id, circle_id) VALUES (%s, %s)
               ON CONFLICT DO NOTHING""",
            (item["user_id"], item["circle_id"]),
        )

    def _upsert_comment(self, item: CommentItem):
        self.cursor.execute(
            """INSERT INTO comments (user_id, album_id, content, created_at)
               VALUES (%s, %s, %s, %s)""",
            (item["user_id"], item["album_id"], item.get("content"), item.get("created_at", datetime.now())),
        )

    def _upsert_owned(self, item: OwnedAlbumItem):
        self.cursor.execute(
            """INSERT INTO owned_albums (user_id, album_id) VALUES (%s, %s)
               ON CONFLICT DO NOTHING""",
            (item["user_id"], item["album_id"]),
        )
