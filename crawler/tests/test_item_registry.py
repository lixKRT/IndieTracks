"""item_registry.py 单元测试。"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from indietracks_spider.item_registry import (
    register,
    get_handler,
    get_all_registered,
    clear_registry,
    register_builtins,
    _resolve_album_tag,
    _resolve_album_circle,
    _resolve_owned,
    _resolve_comment,
    _resolve_user_circle,
    _resolve_workfile,
    _resolve_favorite,
    _resolve_circle_follow,
    _resolve_noop,
    _warn_null_fk,
)
from indietracks_spider.items import (
    AlbumItem, WorkFileItem, CircleItem, AlbumCircleItem,
    TagItem, AlbumTagItem, UserItem, UserCircleItem,
    CommentItem, OwnedAlbumItem, FavoriteItem, CircleFollowItem,
)


class TestRegistry:
    def test_all_builtin_items_registered(self):
        registered = get_all_registered()
        assert TagItem in registered
        assert CircleItem in registered
        assert UserItem in registered
        assert AlbumItem in registered
        assert WorkFileItem in registered
        assert AlbumCircleItem in registered
        assert AlbumTagItem in registered
        assert UserCircleItem in registered
        assert CommentItem in registered
        assert OwnedAlbumItem in registered
        assert FavoriteItem in registered
        assert CircleFollowItem in registered

    def test_registered_count(self):
        assert len(get_all_registered()) == 12

    def test_get_handler_returns_tuple(self):
        handler = get_handler(TagItem)
        assert handler is not None
        assert len(handler) == 2
        resolve_fn, upsert_fn = handler
        assert callable(resolve_fn)
        assert callable(upsert_fn)

    def test_get_handler_unknown_type(self):
        assert get_handler(dict) is None

    def test_register_custom_type(self):
        class CustomItem:
            pass
        resolve_fn = lambda item, repo: None
        upsert_fn = lambda item, repo: None
        register(CustomItem, resolve_fn, upsert_fn)
        assert get_handler(CustomItem) == (resolve_fn, upsert_fn)
        # 清理
        from indietracks_spider.item_registry import _REGISTRY
        del _REGISTRY[CustomItem]

    def test_clear_and_register_builtins(self):
        """验证 clear_registry + register_builtins 可正确恢复。"""
        original_count = len(get_all_registered())
        clear_registry()
        assert len(get_all_registered()) == 0
        register_builtins()
        assert len(get_all_registered()) == original_count


class TestResolveNoop:
    def test_noop_does_nothing(self):
        item = MagicMock()
        repo = MagicMock()
        _resolve_noop(item, repo)
        repo.lookup_album.assert_not_called()


class TestResolveAlbumTag:
    def test_resolves_dizzylab_id(self):
        item = AlbumTagItem()
        item["_dizzylab_id"] = "SW20"
        item["_tag_name"] = "纯音乐"
        item["album_id"] = None
        item["tag_id"] = None
        repo = MagicMock()
        repo.lookup_album.return_value = 42
        repo.lookup_tag.return_value = 3
        _resolve_album_tag(item, repo)
        assert item["album_id"] == 42
        assert item["tag_id"] == 3

    def test_skips_if_already_set(self):
        item = AlbumTagItem()
        item["_dizzylab_id"] = "SW20"
        item["_tag_name"] = "纯音乐"
        item["album_id"] = 99
        item["tag_id"] = 88
        repo = MagicMock()
        _resolve_album_tag(item, repo)
        assert item["album_id"] == 99
        assert item["tag_id"] == 88
        repo.lookup_album.assert_not_called()
        repo.lookup_tag.assert_not_called()


class TestResolveAlbumCircle:
    def test_resolves_both(self):
        item = AlbumCircleItem()
        item["_dizzylab_id"] = "SW20"
        item["_dizzylab_labelid"] = 30
        item["album_id"] = None
        item["circle_id"] = None
        repo = MagicMock()
        repo.lookup_album.return_value = 42
        repo.lookup_circle.return_value = 10
        _resolve_album_circle(item, repo)
        assert item["album_id"] == 42
        assert item["circle_id"] == 10


class TestResolveOwned:
    def test_resolves_both(self):
        item = OwnedAlbumItem()
        item["_dizzylab_user_id"] = 12345
        item["_dizzylab_id"] = "SW20"
        item["user_id"] = None
        item["album_id"] = None
        repo = MagicMock()
        repo.lookup_user.return_value = 7
        repo.lookup_album.return_value = 42
        _resolve_owned(item, repo)
        assert item["user_id"] == 7
        assert item["album_id"] == 42


class TestResolveComment:
    def test_resolves_both(self):
        item = CommentItem()
        item["_dizzylab_user_id"] = 12345
        item["_dizzylab_id"] = "SW20"
        item["user_id"] = None
        item["album_id"] = None
        repo = MagicMock()
        repo.lookup_user.return_value = 7
        repo.lookup_album.return_value = 42
        _resolve_comment(item, repo)
        assert item["user_id"] == 7
        assert item["album_id"] == 42


class TestResolveUserCircle:
    def test_resolves_both(self):
        item = UserCircleItem()
        item["_dizzylab_user_id"] = 12345
        item["_dizzylab_labelid"] = 30
        item["user_id"] = None
        item["circle_id"] = None
        repo = MagicMock()
        repo.lookup_user.return_value = 7
        repo.lookup_circle.return_value = 10
        _resolve_user_circle(item, repo)
        assert item["user_id"] == 7
        assert item["circle_id"] == 10


class TestResolveWorkfile:
    def test_resolves_album(self):
        item = WorkFileItem()
        item["_dizzylab_id"] = "SW20"
        item["album_id"] = None
        repo = MagicMock()
        repo.lookup_album.return_value = 42
        _resolve_workfile(item, repo)
        assert item["album_id"] == 42


class TestResolveFavorite:
    def test_resolves_both(self):
        item = FavoriteItem()
        item["_dizzylab_user_id"] = 12345
        item["_dizzylab_id"] = "SW20"
        item["user_id"] = None
        item["album_id"] = None
        repo = MagicMock()
        repo.lookup_user.return_value = 7
        repo.lookup_album.return_value = 42
        _resolve_favorite(item, repo)
        assert item["user_id"] == 7
        assert item["album_id"] == 42


class TestResolveCircleFollow:
    def test_resolves_both(self):
        item = CircleFollowItem()
        item["_dizzylab_user_id"] = 12345
        item["_dizzylab_labelid"] = 30
        item["user_id"] = None
        item["circle_id"] = None
        repo = MagicMock()
        repo.lookup_user.return_value = 7
        repo.lookup_circle.return_value = 10
        _resolve_circle_follow(item, repo)
        assert item["user_id"] == 7
        assert item["circle_id"] == 10


class TestWarnNullFk:
    def test_warns_on_null(self, caplog):
        import logging
        with caplog.at_level(logging.WARNING):
            item = {"album_id": None, "tag_id": 3}
            _warn_null_fk(item, "TestItem", ["album_id"])
        assert "album_id" in caplog.text
        assert "TestItem" in caplog.text

    def test_no_warning_when_all_set(self, caplog):
        import logging
        with caplog.at_level(logging.WARNING):
            item = {"album_id": 1, "tag_id": 3}
            _warn_null_fk(item, "TestItem", ["album_id", "tag_id"])
        assert "NULL" not in caplog.text
