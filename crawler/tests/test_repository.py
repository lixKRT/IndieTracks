"""repository.py 单元测试。"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from indietracks_spider.repository import Repository
from indietracks_spider.items import (
    AlbumItem, WorkFileItem, CircleItem, AlbumCircleItem,
    TagItem, AlbumTagItem, UserItem, UserCircleItem,
    CommentItem, OwnedAlbumItem, FavoriteItem, CircleFollowItem,
)


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.connected = True
    return db


@pytest.fixture
def repo(mock_db):
    return Repository(mock_db)


# ── Lookup（带缓存）────────────────────────────────────


class TestLookupAlbum:
    def test_cache_hit(self, repo):
        repo._album_id_cache["SW20"] = 42
        assert repo.lookup_album("SW20") == 42

    def test_cache_miss_db_hit(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = (42,)
        result = repo.lookup_album("SW20")
        assert result == 42
        assert repo._album_id_cache["SW20"] == 42

    def test_cache_miss_db_miss(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = None
        assert repo.lookup_album("NONEXIST") is None


class TestLookupCircle:
    def test_cache_hit(self, repo):
        repo._circle_id_cache[30] = 10
        assert repo.lookup_circle(30) == 10

    def test_cache_miss_db_hit(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = (10,)
        result = repo.lookup_circle(30)
        assert result == 10
        assert repo._circle_id_cache[30] == 10


class TestLookupUser:
    def test_cache_hit(self, repo):
        repo._user_id_cache[12345] = 7
        assert repo.lookup_user(12345) == 7

    def test_cache_miss_db_hit(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = (7,)
        result = repo.lookup_user(12345)
        assert result == 7
        assert repo._user_id_cache[12345] == 7


class TestLookupTag:
    def test_cache_hit(self, repo):
        repo._tag_id_cache["纯音乐"] = 3
        assert repo.lookup_tag("纯音乐") == 3

    def test_cache_miss_db_hit(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = (3,)
        result = repo.lookup_tag("纯音乐")
        assert result == 3
        assert repo._tag_id_cache["纯音乐"] == 3


# ── Resolve ────────────────────────────────────────────


class TestResolveAlbumId:
    def test_existing_album(self, repo):
        repo._album_id_cache["SW20"] = 42
        assert repo.resolve_album_id("SW20") == 42

    def test_new_album_insert(self, repo, mock_db):
        mock_db.cursor.fetchone.side_effect = [None, (43,)]
        result = repo.resolve_album_id("NEW", "New Album")
        assert result == 43


class TestResolveCircleIdByName:
    def test_found(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = (10,)
        assert repo.resolve_circle_id_by_name("TestCircle") == 10

    def test_not_found_creates_placeholder(self, repo, mock_db):
        """未找到时创建占位行（dizzylab_labelid = NULL）。"""
        mock_db.cursor.fetchone.side_effect = [None, (42,)]
        result = repo.resolve_circle_id_by_name("NewCircle")
        assert result == 42

    def test_not_found_insert_returns_none(self, repo, mock_db):
        """INSERT 失败时返回 None。"""
        mock_db.cursor.fetchone.return_value = None
        assert repo.resolve_circle_id_by_name("FailCircle") is None


class TestResolveUserDbId:
    def test_delegates_to_lookup(self, repo):
        repo._user_id_cache[12345] = 7
        assert repo.resolve_user_db_id(12345) == 7


# ── Upsert ─────────────────────────────────────────────


class TestUpsertTag:
    def test_cached(self, repo):
        tag = TagItem()
        tag["name"] = "纯音乐"
        repo._tag_id_cache["纯音乐"] = 3
        repo.upsert_tag(tag)
        assert tag["tag_id"] == 3

    def test_empty_name_skips(self, repo, mock_db):
        tag = TagItem()
        tag["name"] = ""
        repo.upsert_tag(tag)
        mock_db.cursor.execute.assert_not_called()

    def test_insert_and_cache(self, repo, mock_db):
        tag = TagItem()
        tag["name"] = "新标签"
        mock_db.cursor.fetchone.return_value = (5,)
        repo.upsert_tag(tag)
        assert tag["tag_id"] == 5
        assert repo._tag_id_cache["新标签"] == 5


class TestUpsertCircle:
    def test_cached(self, repo):
        item = CircleItem()
        item["dizzylab_labelid"] = 30
        repo._circle_id_cache[30] = 10
        repo.upsert_circle(item)
        assert item["circle_id"] == 10

    def test_insert_and_cache(self, repo, mock_db):
        item = CircleItem()
        item["dizzylab_labelid"] = 30
        item["name"] = "Test"
        mock_db.cursor.fetchone.return_value = (10,)
        repo.upsert_circle(item)
        assert item["circle_id"] == 10
        assert repo._circle_id_cache[30] == 10


class TestUpsertUser:
    def test_cached(self, repo):
        item = UserItem()
        item["dizzylab_user_id"] = 12345
        repo._user_id_cache[12345] = 7
        repo.upsert_user(item)
        assert item["user_id"] == 7

    def test_empty_uid_skips(self, repo, mock_db):
        item = UserItem()
        item["dizzylab_user_id"] = None
        repo.upsert_user(item)
        mock_db.cursor.execute.assert_not_called()

    def test_insert_and_cache(self, repo, mock_db):
        item = UserItem()
        item["dizzylab_user_id"] = 99
        item["username"] = "test"
        item["user_role"] = "normal"
        mock_db.cursor.fetchone.return_value = (8,)
        repo.upsert_user(item)
        assert item["user_id"] == 8
        assert repo._user_id_cache[99] == 8


class TestUpsertAlbum:
    def test_cached(self, repo):
        item = AlbumItem()
        item["dizzylab_id"] = "SW20"
        repo._album_id_cache["SW20"] = 42
        repo.upsert_album(item)
        assert item["album_id"] == 42

    def test_insert_and_cache(self, repo, mock_db):
        item = AlbumItem()
        item["dizzylab_id"] = "NEW"
        item["title"] = "Test"
        mock_db.cursor.fetchone.return_value = (43,)
        repo.upsert_album(item)
        assert item["album_id"] == 43
        assert repo._album_id_cache["NEW"] == 43


class TestUpsertWorkfile:
    def test_no_album_id_skips(self, repo, mock_db):
        item = WorkFileItem()
        item["album_id"] = None
        repo.upsert_workfile(item)
        mock_db.cursor.execute.assert_not_called()

    def test_flushes_old_data_once(self, repo, mock_db):
        item = WorkFileItem()
        item["album_id"] = 42
        mock_db.cursor.fetchone.return_value = (1,)
        repo.upsert_workfile(item)
        # 第一次应该 DELETE + INSERT
        assert mock_db.cursor.execute.call_count == 2
        assert 42 in repo._workfile_flushed

    def test_second_call_no_delete(self, repo, mock_db):
        repo._workfile_flushed.add(42)
        item = WorkFileItem()
        item["album_id"] = 42
        mock_db.cursor.fetchone.return_value = (1,)
        repo.upsert_workfile(item)
        # 第二次只 INSERT，不 DELETE
        mock_db.cursor.execute.assert_called_once()


class TestUpsertAssociation:
    def test_album_circle(self, repo, mock_db):
        item = AlbumCircleItem()
        item["album_id"] = 1
        item["circle_id"] = 2
        repo.upsert_album_circle(item)
        mock_db.cursor.execute.assert_called_once()

    def test_album_tag(self, repo, mock_db):
        item = AlbumTagItem()
        item["album_id"] = 1
        item["tag_id"] = 3
        repo.upsert_album_tag(item)
        mock_db.cursor.execute.assert_called_once()

    def test_user_circle(self, repo, mock_db):
        item = UserCircleItem()
        item["user_id"] = 1
        item["circle_id"] = 2
        repo.upsert_user_circle(item)
        mock_db.cursor.execute.assert_called_once()

    def test_comment(self, repo, mock_db):
        item = CommentItem()
        item["user_id"] = 1
        item["album_id"] = 2
        item["content"] = "test"
        repo.upsert_comment(item)
        mock_db.cursor.execute.assert_called_once()

    def test_owned(self, repo, mock_db):
        item = OwnedAlbumItem()
        item["user_id"] = 1
        item["album_id"] = 2
        repo.upsert_owned(item)
        mock_db.cursor.execute.assert_called_once()

    def test_favorite(self, repo, mock_db):
        item = FavoriteItem()
        item["user_id"] = 1
        item["album_id"] = 2
        repo.upsert_favorite(item)
        mock_db.cursor.execute.assert_called_once()

    def test_circle_follow(self, repo, mock_db):
        item = CircleFollowItem()
        item["user_id"] = 1
        item["circle_id"] = 2
        repo.upsert_circle_follow(item)
        mock_db.cursor.execute.assert_called_once()


# ── 直接 SQL 操作 ──────────────────────────────────────


class TestUpdateRole:
    def test_update_role(self, repo, mock_db):
        repo.update_role(12345, "staff")
        mock_db.cursor.execute.assert_called_once()

    def test_update_role_no_return(self, repo, mock_db):
        """update_role 不再返回值。"""
        result = repo.update_role(12345, "staff")
        assert result is None

    def test_update_role_if_normal_skips_staff(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = ("staff",)
        result = repo.update_role_if_normal(12345, "pro")
        assert result is False

    def test_update_role_if_normal_writes_normal(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = ("normal",)
        result = repo.update_role_if_normal(12345, "pro")
        assert result is True

    def test_update_role_if_normal_writes_none(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = (None,)
        result = repo.update_role_if_normal(12345, "pro")
        assert result is True


class TestUpdateCircleInfo:
    def test_by_circle_id(self, repo, mock_db):
        repo.update_circle_info(10, "desc", "key", 5)
        mock_db.cursor.execute.assert_called_once()

    def test_by_labelid(self, repo, mock_db):
        repo.update_circle_info_by_labelid(30, "desc", "key", 5)
        mock_db.cursor.execute.assert_called_once()


class TestUpdateUserAvatar:
    def test_updates_avatar(self, repo, mock_db):
        repo.update_user_avatar(12345, "avatars/user.jpg")
        mock_db.cursor.execute.assert_called_once()


class TestMarkUserCrawled:
    def test_marks_crawled(self, repo, mock_db):
        repo.mark_user_crawled(12345)
        mock_db.cursor.execute.assert_called_once()


class TestIsAlbumComplete:
    def test_complete(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = ("Some Title",)
        assert repo.is_album_complete("SW20") is True

    def test_incomplete_null(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = (None,)
        assert repo.is_album_complete("SW20") is False

    def test_nonexistent(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = None
        assert repo.is_album_complete("NONEXIST") is False

    def test_empty_string_is_complete(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = ("",)
        assert repo.is_album_complete("SW20") is True


class TestGetCircleUpToDate:
    def test_up_to_date(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = (5, 5)
        assert repo.get_circle_up_to_date(10) is True

    def test_not_up_to_date(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = (5, 3)
        assert repo.get_circle_up_to_date(10) is False

    def test_no_circle(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = None
        assert repo.get_circle_up_to_date(10) is False


class TestGetUsersForCrawling:
    def test_with_target_ids(self, repo, mock_db):
        mock_db.cursor.fetchall.return_value = [(1, "user1"), (2, "user2")]
        result = repo.get_users_for_crawling(target_ids=[1, 2])
        assert len(result) == 2

    def test_full_mode(self, repo, mock_db):
        mock_db.cursor.fetchall.return_value = [(1, "user1")]
        result = repo.get_users_for_crawling(mode="full")
        assert len(result) == 1


class TestGetAllCircles:
    def test_returns_circles(self, repo, mock_db):
        mock_db.cursor.fetchall.return_value = [(1, 30, "Circle1")]
        result = repo.get_all_circles()
        assert len(result) == 1


class TestIsUserPageFresh:
    def test_fresh(self, repo, mock_db):
        from datetime import datetime, timedelta, timezone
        recent = datetime.now(timezone.utc) - timedelta(days=5)
        mock_db.cursor.fetchone.return_value = (recent,)
        assert repo.is_user_page_fresh(12345, days=30) is True

    def test_stale(self, repo, mock_db):
        from datetime import datetime, timedelta, timezone
        old = datetime.now(timezone.utc) - timedelta(days=60)
        mock_db.cursor.fetchone.return_value = (old,)
        assert repo.is_user_page_fresh(12345, days=30) is False

    def test_never_crawled(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = (None,)
        assert repo.is_user_page_fresh(12345, days=30) is False

    def test_no_user(self, repo, mock_db):
        mock_db.cursor.fetchone.return_value = None
        assert repo.is_user_page_fresh(12345, days=30) is False


class TestGetUsersForCrawlingWithAny:
    def test_uses_any_syntax(self, repo, mock_db):
        """验证使用 psycopg2 的 ANY(%s) 而非 f-string。"""
        mock_db.cursor.fetchall.return_value = [(1, "u1")]
        repo.get_users_for_crawling(target_ids=[1, 2, 3])
        # 验证 execute 被调用时使用了 ANY(%s)
        call_args = mock_db.cursor.execute.call_args
        sql = call_args[0][0]
        assert "ANY(%s)" in sql
        # 参数应是单个 list，不是 tuple of individual values
        params = call_args[0][1]
        assert params == ([1, 2, 3],)
