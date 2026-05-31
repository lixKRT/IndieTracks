"""Item 注册表 — 消灭 Pipeline 中的 isinstance 链。

每种 Item 注册 (handler, resolver) 对，Pipeline 变成薄调度层。
新增 Item 只需在 items.py 定义 + 调用 register() 注册，不碰 Pipeline 主体。
"""

from __future__ import annotations

import logging
from typing import Callable

from indietracks_spider.items import (
    AlbumItem, WorkFileItem, CircleItem, AlbumCircleItem,
    TagItem, AlbumTagItem, UserItem, UserCircleItem,
    CommentItem, OwnedAlbumItem, FavoriteItem, CircleFollowItem,
)

logger = logging.getLogger(__name__)

# 注册表：item_type → (resolve_fn, upsert_fn)
# resolve_fn(item, repo) — 解析临时关联字段
# upsert_fn(item, repo) — 写入数据库
_REGISTRY: dict[type, tuple[Callable, Callable]] = {}


def register(item_type: type, resolve_fn: Callable, upsert_fn: Callable) -> None:
    """注册 Item 类型的处理函数。"""
    _REGISTRY[item_type] = (resolve_fn, upsert_fn)


def get_handler(item_type: type) -> tuple[Callable, Callable] | None:
    """获取 Item 类型的处理函数。"""
    return _REGISTRY.get(item_type)


def get_all_registered() -> dict[type, tuple[Callable, Callable]]:
    """返回所有已注册的 Item 类型（用于测试）。"""
    return dict(_REGISTRY)


def clear_registry() -> None:
    """清空注册表（测试用 teardown）。调用后需 register_builtins() 恢复。"""
    _REGISTRY.clear()


def register_builtins() -> None:
    """注册所有内置 Item 类型（公开方法，可在测试 teardown 中调用）。"""
    _register_builtins()


# ── 内置 resolve 函数 ────────────────────────────────────


def _resolve_album_tag(item, repo) -> None:
    """AlbumTagItem: _tag_name → tag_id, _dizzylab_id → album_id"""
    if not item.get("album_id") and item.get("_dizzylab_id"):
        item["album_id"] = repo.lookup_album(item["_dizzylab_id"])
    if not item.get("tag_id") and item.get("_tag_name"):
        item["tag_id"] = repo.lookup_tag(item["_tag_name"])
    _warn_null_fk(item, "AlbumTagItem", ["album_id", "tag_id"])


def _resolve_album_circle(item, repo) -> None:
    """AlbumCircleItem: _dizzylab_labelid → circle_id, _dizzylab_id → album_id"""
    if not item.get("album_id") and item.get("_dizzylab_id"):
        item["album_id"] = repo.lookup_album(item["_dizzylab_id"])
    if not item.get("circle_id") and item.get("_dizzylab_labelid"):
        item["circle_id"] = repo.lookup_circle(item["_dizzylab_labelid"])
    _warn_null_fk(item, "AlbumCircleItem", ["album_id", "circle_id"])


def _resolve_owned(item, repo) -> None:
    """OwnedAlbumItem: _dizzylab_user_id → user_id, _dizzylab_id → album_id"""
    if not item.get("user_id") and item.get("_dizzylab_user_id"):
        item["user_id"] = repo.lookup_user(item["_dizzylab_user_id"])
    if not item.get("album_id") and item.get("_dizzylab_id"):
        item["album_id"] = repo.lookup_album(item["_dizzylab_id"])
    _warn_null_fk(item, "OwnedAlbumItem", ["user_id", "album_id"])


def _resolve_comment(item, repo) -> None:
    """CommentItem: _dizzylab_user_id → user_id, _dizzylab_id → album_id"""
    if not item.get("user_id") and item.get("_dizzylab_user_id"):
        item["user_id"] = repo.lookup_user(item["_dizzylab_user_id"])
    if not item.get("album_id") and item.get("_dizzylab_id"):
        item["album_id"] = repo.lookup_album(item["_dizzylab_id"])
    _warn_null_fk(item, "CommentItem", ["user_id", "album_id"])


def _resolve_user_circle(item, repo) -> None:
    """UserCircleItem: _dizzylab_user_id → user_id, _dizzylab_labelid → circle_id"""
    if not item.get("user_id") and item.get("_dizzylab_user_id"):
        item["user_id"] = repo.lookup_user(item["_dizzylab_user_id"])
    if not item.get("circle_id") and item.get("_dizzylab_labelid"):
        item["circle_id"] = repo.lookup_circle(item["_dizzylab_labelid"])
    _warn_null_fk(item, "UserCircleItem", ["user_id", "circle_id"])


def _resolve_workfile(item, repo) -> None:
    """WorkFileItem: _dizzylab_id → album_id"""
    if not item.get("album_id") and item.get("_dizzylab_id"):
        item["album_id"] = repo.lookup_album(item["_dizzylab_id"])
    _warn_null_fk(item, "WorkFileItem", ["album_id"])


def _resolve_favorite(item, repo) -> None:
    """FavoriteItem: _dizzylab_user_id → user_id, _dizzylab_id → album_id"""
    if not item.get("user_id") and item.get("_dizzylab_user_id"):
        item["user_id"] = repo.lookup_user(item["_dizzylab_user_id"])
    if not item.get("album_id") and item.get("_dizzylab_id"):
        item["album_id"] = repo.lookup_album(item["_dizzylab_id"])
    _warn_null_fk(item, "FavoriteItem", ["user_id", "album_id"])


def _resolve_circle_follow(item, repo) -> None:
    """CircleFollowItem: _dizzylab_user_id → user_id, _dizzylab_labelid → circle_id"""
    if not item.get("user_id") and item.get("_dizzylab_user_id"):
        item["user_id"] = repo.lookup_user(item["_dizzylab_user_id"])
    if not item.get("circle_id") and item.get("_dizzylab_labelid"):
        item["circle_id"] = repo.lookup_circle(item["_dizzylab_labelid"])
    _warn_null_fk(item, "CircleFollowItem", ["user_id", "circle_id"])


def _resolve_noop(item, repo) -> None:
    """无需解析的 Item（TagItem, CircleItem, UserItem, AlbumItem）。"""
    pass


def _warn_null_fk(item, item_name: str, fk_fields: list[str]) -> None:
    """FK 解析失败时发出警告（不再静默 None）。"""
    for field in fk_fields:
        if item.get(field) is None:
            logger.warning(
                "[%s] FK 字段 '%s' 解析为 NULL，可能导致孤立行。item=%s",
                item_name, field, dict(item),
            )


# ── 内置 upsert 函数（代理到 Repository）──────────────────


def _upsert_tag(item, repo) -> None:
    repo.upsert_tag(item)


def _upsert_circle(item, repo) -> None:
    repo.upsert_circle(item)


def _upsert_user(item, repo) -> None:
    repo.upsert_user(item)


def _upsert_album(item, repo) -> None:
    repo.upsert_album(item)


def _upsert_workfile(item, repo) -> None:
    repo.upsert_workfile(item)


def _upsert_album_circle(item, repo) -> None:
    repo.upsert_album_circle(item)


def _upsert_album_tag(item, repo) -> None:
    repo.upsert_album_tag(item)


def _upsert_user_circle(item, repo) -> None:
    repo.upsert_user_circle(item)


def _upsert_comment(item, repo) -> None:
    repo.upsert_comment(item)


def _upsert_owned(item, repo) -> None:
    repo.upsert_owned(item)


def _upsert_favorite(item, repo) -> None:
    repo.upsert_favorite(item)


def _upsert_circle_follow(item, repo) -> None:
    repo.upsert_circle_follow(item)


# ── 自动注册所有内置 Item 类型 ────────────────────────────


def _register_builtins() -> None:
    """注册所有内置 Item 类型。"""
    register(TagItem, _resolve_noop, _upsert_tag)
    register(CircleItem, _resolve_noop, _upsert_circle)
    register(UserItem, _resolve_noop, _upsert_user)
    register(AlbumItem, _resolve_noop, _upsert_album)
    register(WorkFileItem, _resolve_workfile, _upsert_workfile)
    register(AlbumCircleItem, _resolve_album_circle, _upsert_album_circle)
    register(AlbumTagItem, _resolve_album_tag, _upsert_album_tag)
    register(UserCircleItem, _resolve_user_circle, _upsert_user_circle)
    register(CommentItem, _resolve_comment, _upsert_comment)
    register(OwnedAlbumItem, _resolve_owned, _upsert_owned)
    register(FavoriteItem, _resolve_favorite, _upsert_favorite)
    register(CircleFollowItem, _resolve_circle_follow, _upsert_circle_follow)


_register_builtins()
