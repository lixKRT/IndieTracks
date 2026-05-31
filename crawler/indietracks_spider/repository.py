"""统一持久化模块 — Repository 层。

所有 DB 写入/查询通过此模块，消除蜘蛛直连 SQL 和 Pipeline 之间的重复。
提供内存缓存，避免对同一 dizzylab_id 反复 SELECT。
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from indietracks_spider.utils.db import DbConnection

logger = logging.getLogger(__name__)


class Repository:
    """统一的数据库读写层。

    用法:
        db = DbConnection(autocommit=False)
        db.connect()
        repo = Repository(db)
        repo.upsert_album(item)
        repo.commit()
    """

    def __init__(self, db: DbConnection):
        self._db = db
        # 内存映射缓存：避免对同一 dizzylab_id 反复 SELECT
        self._album_id_cache: dict[str, int] = {}       # dizzylab_id → album_id
        self._circle_id_cache: dict[int, int] = {}       # dizzylab_labelid → circle_id
        self._user_id_cache: dict[int, int] = {}         # dizzylab_user_id → user_id
        self._tag_id_cache: dict[str, int] = {}          # tag_name → tag_id
        # 已插入 work_files 的 album_id，用于清旧数据
        self._workfile_flushed: set[int] = set()

    @property
    def cursor(self):
        return self._db.cursor

    def commit(self) -> None:
        self._db.commit()

    def rollback(self) -> None:
        self._db.rollback()

    # ── FK 解析（带缓存）────────────────────────────────

    def lookup_circle(self, labelid: int) -> int | None:
        """缓存未命中时从 DB 查 circle_id，查到则回填缓存。"""
        if labelid in self._circle_id_cache:
            return self._circle_id_cache[labelid]
        self.cursor.execute(
            "SELECT circle_id FROM circles WHERE dizzylab_labelid = %s", (labelid,)
        )
        row = self.cursor.fetchone()
        if row:
            self._circle_id_cache[labelid] = row[0]
            return row[0]
        return None

    def lookup_album(self, dizzylab_id: str) -> int | None:
        """缓存未命中时从 DB 查 album_id，查到则回填缓存。"""
        if dizzylab_id in self._album_id_cache:
            return self._album_id_cache[dizzylab_id]
        self.cursor.execute(
            "SELECT album_id FROM albums WHERE dizzylab_id = %s", (dizzylab_id,)
        )
        row = self.cursor.fetchone()
        if row:
            self._album_id_cache[dizzylab_id] = row[0]
            return row[0]
        return None

    def lookup_user(self, dizzylab_user_id: int) -> int | None:
        """缓存未命中时从 DB 查 user_id，查到则回填缓存。"""
        if dizzylab_user_id in self._user_id_cache:
            return self._user_id_cache[dizzylab_user_id]
        self.cursor.execute(
            "SELECT user_id FROM users WHERE dizzylab_user_id = %s", (dizzylab_user_id,)
        )
        row = self.cursor.fetchone()
        if row:
            self._user_id_cache[dizzylab_user_id] = row[0]
            return row[0]
        return None

    def lookup_tag(self, tag_name: str) -> int | None:
        """缓存未命中时从 DB 查 tag_id，查到则回填缓存。"""
        if tag_name in self._tag_id_cache:
            return self._tag_id_cache[tag_name]
        self.cursor.execute(
            "SELECT tag_id FROM tags WHERE name = %s", (tag_name,)
        )
        row = self.cursor.fetchone()
        if row:
            self._tag_id_cache[tag_name] = row[0]
            return row[0]
        return None

    # ── Resolve（查找或创建占位行）────────────────────────

    def resolve_album_id(self, dizzylab_id: str, title: str | None = None) -> int | None:
        """查找或创建 album 占位行，返回 album_id。"""
        existing = self.lookup_album(dizzylab_id)
        if existing:
            return existing
        self.cursor.execute(
            """INSERT INTO albums (dizzylab_id, title) VALUES (%s, %s)
               ON CONFLICT (dizzylab_id) DO NOTHING
               RETURNING album_id""",
            (dizzylab_id, title or dizzylab_id),
        )
        row = self.cursor.fetchone()
        if row:
            self._album_id_cache[dizzylab_id] = row[0]
            return row[0]
        # CONFLICT 触发了 DO NOTHING，重新查询
        return self.lookup_album(dizzylab_id)

    def resolve_circle_id_by_name(self, name: str) -> int | None:
        """根据社团名查找或创建占位行，返回 circle_id。

        circles 表的 UNIQUE 在 dizzylab_labelid 上，name 不唯一。
        查找时先精确匹配 name，未命中则 INSERT 占位行（dizzylab_labelid = NULL）。
        """
        self.cursor.execute(
            "SELECT circle_id FROM circles WHERE name = %s", (name,)
        )
        row = self.cursor.fetchone()
        if row:
            return row[0]
        # 不存在则创建占位行（dizzylab_labelid 为 NULL，后续 circle 爬虫补全）
        self.cursor.execute(
            "INSERT INTO circles (name) VALUES (%s) RETURNING circle_id",
            (name,),
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def resolve_user_db_id(self, dizzylab_user_id: int) -> int | None:
        """查找 user_id（db 主键）。"""
        return self.lookup_user(dizzylab_user_id)

    # ── Upsert 各表 ─────────────────────────────────────
    # 统一使用 item.get() 访问字段（scrapy.Item 兼容）

    def upsert_tag(self, item) -> None:
        name = item.get("name")
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

    def upsert_circle(self, item) -> None:
        lid = item.get("dizzylab_labelid")
        if lid in self._circle_id_cache:
            item["circle_id"] = self._circle_id_cache[lid]
            return
        self.cursor.execute(
            """INSERT INTO circles (dizzylab_labelid, name, description, logo_url)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (dizzylab_labelid) DO UPDATE
                 SET name=EXCLUDED.name,
                     description=COALESCE(EXCLUDED.description, circles.description),
                     logo_url=COALESCE(EXCLUDED.logo_url, circles.logo_url)
               RETURNING circle_id""",
            (lid, item.get("name"), item.get("description"), item.get("logo_url")),
        )
        row = self.cursor.fetchone()
        if row:
            item["circle_id"] = row[0]
            self._circle_id_cache[lid] = row[0]

    def upsert_user(self, item) -> None:
        uid = item.get("dizzylab_user_id")
        if not uid:
            return
        if uid in self._user_id_cache:
            item["user_id"] = self._user_id_cache[uid]
            return
        role = item.get("user_role", "normal")
        self.cursor.execute(
            """INSERT INTO users (dizzylab_user_id, username, avatar_url, user_role)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (dizzylab_user_id) DO UPDATE
                 SET username=EXCLUDED.username,
                     avatar_url=COALESCE(EXCLUDED.avatar_url, users.avatar_url),
                     user_role = CASE
                       WHEN users.user_role = 'staff' THEN 'staff'
                       ELSE EXCLUDED.user_role
                     END
               RETURNING user_id""",
            (uid, item.get("username"), item.get("avatar_url"), role),
        )
        row = self.cursor.fetchone()
        if row:
            item["user_id"] = row[0]
            self._user_id_cache[uid] = row[0]

    def upsert_album(self, item) -> None:
        did = item.get("dizzylab_id")
        if did in self._album_id_cache:
            item["album_id"] = self._album_id_cache[did]
            return
        self.cursor.execute(
            """INSERT INTO albums (dizzylab_id, title, info_title, info_content, price, cover_url, publish_date)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (dizzylab_id) DO UPDATE
                 SET title=EXCLUDED.title,
                     info_title=COALESCE(EXCLUDED.info_title, albums.info_title),
                     info_content=COALESCE(EXCLUDED.info_content, albums.info_content),
                     price=EXCLUDED.price,
                     cover_url=COALESCE(EXCLUDED.cover_url, albums.cover_url),
                     publish_date=COALESCE(EXCLUDED.publish_date, albums.publish_date)
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

    def upsert_workfile(self, item) -> None:
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

    def upsert_album_circle(self, item) -> None:
        self.cursor.execute(
            """INSERT INTO album_circles (album_id, circle_id) VALUES (%s, %s)
               ON CONFLICT DO NOTHING""",
            (item.get("album_id"), item.get("circle_id")),
        )

    def upsert_album_tag(self, item) -> None:
        self.cursor.execute(
            """INSERT INTO album_tags (album_id, tag_id) VALUES (%s, %s)
               ON CONFLICT DO NOTHING""",
            (item.get("album_id"), item.get("tag_id")),
        )

    def upsert_user_circle(self, item) -> None:
        self.cursor.execute(
            """INSERT INTO user_circles (user_id, circle_id) VALUES (%s, %s)
               ON CONFLICT DO NOTHING""",
            (item.get("user_id"), item.get("circle_id")),
        )

    def upsert_comment(self, item) -> None:
        self.cursor.execute(
            """INSERT INTO comments (user_id, album_id, content, created_at)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (user_id, album_id, content) DO NOTHING""",
            (item.get("user_id"), item.get("album_id"), item.get("content"), item.get("created_at", datetime.now(timezone.utc))),
        )

    def upsert_owned(self, item) -> None:
        self.cursor.execute(
            """INSERT INTO owned_albums (user_id, album_id) VALUES (%s, %s)
               ON CONFLICT DO NOTHING""",
            (item.get("user_id"), item.get("album_id")),
        )

    def upsert_favorite(self, item) -> None:
        self.cursor.execute(
            """INSERT INTO favorites (user_id, album_id) VALUES (%s, %s)
               ON CONFLICT DO NOTHING""",
            (item.get("user_id"), item.get("album_id")),
        )

    def upsert_circle_follow(self, item) -> None:
        self.cursor.execute(
            """INSERT INTO circle_follows (user_id, circle_id) VALUES (%s, %s)
               ON CONFLICT DO NOTHING""",
            (item.get("user_id"), item.get("circle_id")),
        )

    # ── 直接 SQL 操作（供蜘蛛使用）─────────────────────────

    def update_role(self, dizzylab_user_id: int, role: str) -> None:
        """更新用户角色（staff 不可降级）。"""
        self.cursor.execute(
            """INSERT INTO users (dizzylab_user_id, username, user_role)
               VALUES (%s, %s, %s)
               ON CONFLICT (dizzylab_user_id) DO UPDATE
                 SET user_role = CASE
                   WHEN users.user_role = 'staff' THEN 'staff'
                   ELSE EXCLUDED.user_role
                 END""",
            (dizzylab_user_id, f"user_{dizzylab_user_id}", role),
        )

    def update_role_if_normal(self, dizzylab_user_id: int, role: str) -> bool:
        """incremental 模式：仅更新 role 为空或 normal 的用户。返回是否实际写入。"""
        self.cursor.execute(
            "SELECT user_role FROM users WHERE dizzylab_user_id = %s",
            (dizzylab_user_id,),
        )
        row = self.cursor.fetchone()
        if row and row[0] and row[0] != "normal":
            return False  # 跳过
        self.update_role(dizzylab_user_id, role)
        return True

    def update_circle_info(self, circle_id: int, description: str, logo_key: str | None, member_count: int) -> None:
        """更新社团描述、logo、成员数（by circle_id）。"""
        self.cursor.execute(
            """UPDATE circles
               SET description = %s,
                   logo_url = COALESCE(%s, logo_url),
                   member_count = %s
               WHERE circle_id = %s""",
            (description, logo_key, member_count, circle_id),
        )

    def update_circle_info_by_labelid(self, labelid: int, description: str, logo_key: str | None, member_count: int) -> None:
        """更新社团描述、logo、成员数（by dizzylab_labelid）。"""
        self.cursor.execute(
            """UPDATE circles
               SET description = %s,
                   logo_url = COALESCE(%s, logo_url),
                   member_count = %s
               WHERE dizzylab_labelid = %s""",
            (description, logo_key, member_count, labelid),
        )

    def update_user_avatar(self, dizzylab_user_id: int, avatar_key: str) -> None:
        """更新用户头像。"""
        self.cursor.execute(
            "UPDATE users SET avatar_url = %s WHERE dizzylab_user_id = %s",
            (avatar_key, dizzylab_user_id),
        )

    def mark_user_crawled(self, dizzylab_user_id: int) -> None:
        """标记用户页面已爬取。"""
        self.cursor.execute(
            "UPDATE users SET userpage_crawled_at = %s WHERE dizzylab_user_id = %s",
            (datetime.now(timezone.utc), dizzylab_user_id),
        )

    def is_album_complete(self, dizzylab_id: str) -> bool:
        """检查专辑是否数据完整（info_title IS NOT NULL）。"""
        self.cursor.execute(
            "SELECT info_title FROM albums WHERE dizzylab_id = %s",
            (dizzylab_id,),
        )
        row = self.cursor.fetchone()
        return row is not None and row[0] is not None

    def is_user_page_fresh(self, dizzylab_user_id: int, days: int = 30) -> bool:
        """检查用户页面是否在 N 天内已爬取。"""
        self.cursor.execute(
            "SELECT userpage_crawled_at FROM users WHERE dizzylab_user_id = %s",
            (dizzylab_user_id,),
        )
        row = self.cursor.fetchone()
        if not row or not row[0]:
            return False
        age = datetime.now(timezone.utc) - row[0].replace(tzinfo=timezone.utc)
        return age.days < days

    def get_circle_up_to_date(self, circle_id: int) -> bool:
        """检查社团成员数是否与上次爬取一致。"""
        self.cursor.execute(
            """SELECT c.member_count, COUNT(uc.user_id)
               FROM circles c
               LEFT JOIN user_circles uc ON uc.circle_id = c.circle_id
               WHERE c.circle_id = %s
               GROUP BY c.circle_id""",
            (circle_id,),
        )
        row = self.cursor.fetchone()
        if row is None:
            return False
        stored_count, actual_count = row
        return stored_count is not None and stored_count == actual_count

    def get_users_for_crawling(self, target_ids: list[int] | None = None,
                                mode: str = "full") -> list[tuple]:
        """获取待处理用户列表。"""
        if target_ids:
            self.cursor.execute(
                "SELECT dizzylab_user_id, username FROM users WHERE dizzylab_user_id = ANY(%s) ORDER BY dizzylab_user_id",
                (target_ids,),
            )
        else:
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            if mode == "incremental":
                self.cursor.execute(
                    """SELECT dizzylab_user_id, username FROM users
                       WHERE userpage_crawled_at IS NULL
                          OR userpage_crawled_at < %s
                       ORDER BY dizzylab_user_id""",
                    (cutoff,),
                )
            else:
                self.cursor.execute(
                    "SELECT dizzylab_user_id, username FROM users ORDER BY dizzylab_user_id"
                )
        return self.cursor.fetchall()

    def get_all_circles(self) -> list[tuple]:
        """获取所有社团列表。"""
        self.cursor.execute(
            "SELECT circle_id, dizzylab_labelid, name FROM circles ORDER BY circle_id"
        )
        return self.cursor.fetchall()
