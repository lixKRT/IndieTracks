"""
BaseAlbumSpider — 专辑爬虫基类。

提取 album_bulk / album_incremental / album_test 共享的解析方法：
- parse_album_detail（含 MinIO 音频下载）
- parse_buyers / parse_comments / parse_circle_detail
- _album_is_complete（通过 Repository）

使用 DbSpiderMixin 统一 DB 连接管理。
"""

from __future__ import annotations

import json
import re
import logging
from datetime import datetime, timezone
from urllib.parse import quote

import scrapy

from indietracks_spider.db_mixin import DbSpiderMixin
from indietracks_spider.items import (
    AlbumItem,
    WorkFileItem,
    CircleItem,
    AlbumCircleItem,
    TagItem,
    AlbumTagItem,
    UserItem,
    UserCircleItem,
    CommentItem,
    OwnedAlbumItem,
)
from indietracks_spider.utils.constants import BASE, API_DISCS, PAGE_SIZE
from indietracks_spider.utils.delay import schedule_track_delay
from indietracks_spider.utils.storage import get_storage_backend
from indietracks_spider.utils.circle import extract_circle_info, yield_circle_members
from indietracks_spider.utils.parsing import (
    extract_user_id,
    parse_date_cn,
    parse_track_title,
    safe_json_load,
    check_response_ok,
)

logger = logging.getLogger(__name__)


class BaseAlbumSpider(DbSpiderMixin, scrapy.Spider):
    """专辑爬虫基类——子类只需实现 start_requests 和 parse_disc_list。"""

    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    # ── 子类可覆盖的属性 ──────────────────────────────

    _track_min: int = 1
    _track_random_max: int = 3

    # ── DB 检查 ──────────────────────────────────────

    def _album_is_complete(self, dizzylab_id: str) -> bool:
        self._ensure_db()
        return self.repo.is_album_complete(dizzylab_id)

    # ── API 工具方法 ─────────────────────────────────

    @staticmethod
    def make_disc_request(start: int, callback, meta: dict = None, **kwargs):
        """构造专辑列表 API 请求。"""
        end = start + PAGE_SIZE
        return scrapy.Request(
            f"{API_DISCS}?l={start}&r={end}&sort=ad&type=album",
            callback=callback,
            meta=meta or {},
            dont_filter=True,
            **kwargs,
        )

    @staticmethod
    def _parse_discs_response(response) -> list[dict] | None:
        """解析专辑列表 API 响应，返回 discs 列表或 None（失败时）。"""
        if not check_response_ok(response):
            return None
        data = safe_json_load(response)
        if data is None:
            return None
        return data.get("discs", [])

    # ── 专辑详情页 ───────────────────────────────────

    # ── 专辑详情页 ───────────────────────────────────

    def parse_album_detail(self, response):
        disc = response.meta["disc"]
        slug = disc["id"]
        storage = get_storage_backend()

        # ── AlbumItem ──
        album = AlbumItem()
        album["dizzylab_id"] = slug
        album["title"] = disc.get("title", "")
        try:
            album["price"] = float(disc.get("price", 0))
        except (ValueError, TypeError):
            album["price"] = 0.0
        album["cover_url"] = disc.get("cover", "")

        # info_title: 专辑介绍段落
        info_p = response.xpath("//p[@class='text-left' and contains(@style,'margin-top:32px')]")
        if info_p:
            raw_html = info_p[0].get()
            text = re.sub(r'<br\s*/?>', '\n', raw_html)
            text = re.sub(r'<[^>]+>', '', text)
            album["info_title"] = text.strip()
        else:
            album["info_title"] = ""

        # info_content: <h3> 区段
        info_h3 = response.xpath("//h3[@class='text-left' and not(contains(@class,'p-1'))]")
        if info_h3:
            raw_h3 = info_h3[0].get()
            text = re.sub(r'<br\s*/?>', '\n', raw_h3)
            text = re.sub(r'<[^>]+>', '', text)
            album["info_content"] = text.strip()
        else:
            album["info_content"] = ""

        pub_text = response.xpath("//text()[contains(., '发布于')]").get()
        pub_date = parse_date_cn(pub_text) if pub_text else None
        album["publish_date"] = pub_date

        cover = response.xpath("//img[@id='imgsrc0']/@data-src").get()
        if cover:
            album["cover_url"] = cover

        # 封面上传 MinIO
        cover_key = storage.upload_image(album.get("cover_url", ""))
        if cover_key:
            album["cover_url"] = cover_key

        yield album

        # ── WorkFile (下载 + 上传 MinIO) ──
        track_lis = response.xpath("//ul[contains(@class,'playlist--list')]/li")
        for li in track_lis:
            data_id = li.xpath("./@data-id").get()
            data_audio = li.xpath("./@data-audio").get()
            title_text = li.xpath(".//span[@class='t-title']/text()").get()

            sort_order = int(data_id) + 1 if data_id is not None else 0

            obj_key = None
            file_size = 0
            if data_audio:
                result = storage.upload_audio(data_audio, slug, sort_order)
                if result:
                    obj_key, file_size = result
                else:
                    self.logger.warning(
                        "  [跳过] 曲目 %d 音频下载失败: %s", sort_order, title_text or "?"
                    )
                    continue

            wf = WorkFileItem()
            wf["album_id"] = None
            wf["_dizzylab_id"] = slug
            wf["file_type"] = "preview"
            wf["file_size"] = file_size
            wf["sort_order"] = sort_order
            wf["object_key"] = obj_key or data_audio

            if title_text:
                file_name, track_length = parse_track_title(title_text.strip())
                wf["file_name"] = file_name
                wf["track_length"] = track_length

            yield wf

            schedule_track_delay(self._track_min, self._track_random_max)

        # ── Tag + AlbumTag ──
        tag_as = response.xpath("//h4[@class='text-left']/a")
        for a in tag_as:
            raw = a.xpath("./text()").get("")
            clean = raw.lstrip("#").strip()
            if clean:
                tag = TagItem()
                tag["name"] = clean
                yield tag

                at = AlbumTagItem()
                at["album_id"] = None
                at["tag_id"] = None
                at["_tag_name"] = clean
                at["_dizzylab_id"] = slug
                yield at

        # ── Circle + AlbumCircle ──
        labelname = disc.get("label", "")
        labelid = disc.get("labelid")
        if labelid:
            circle = CircleItem()
            circle["dizzylab_labelid"] = int(labelid)
            circle["name"] = labelname
            logo_url = disc.get("labelcover", "")
            logo_key = storage.upload_image(logo_url)
            circle["logo_url"] = logo_key or logo_url
            circle["description"] = None
            yield circle

            ac = AlbumCircleItem()
            ac["album_id"] = None
            ac["circle_id"] = None
            ac["_dizzylab_labelid"] = int(labelid)
            ac["_dizzylab_id"] = slug
            yield ac

        # ── 子请求 ──
        yield scrapy.Request(
            f"{BASE}/albums/getbuyers/?discid={slug}&l=0&r=60",
            callback=self.parse_buyers,
            meta={"_dizzylab_id": slug},
        )

        yield scrapy.Request(
            f"{BASE}/albums/getdisccomment/?discid={slug}&l=0&r=20",
            callback=self.parse_comments,
            meta={"_dizzylab_id": slug},
        )

        if labelname:
            yield scrapy.Request(
                f"{BASE}/l/{quote(labelname)}/",
                callback=self.parse_circle_detail,
                meta={
                    "_dizzylab_labelid": int(labelid) if labelid else None,
                    "_labelname": labelname,
                },
            )

        # 子类钩子：专辑间延迟等
        self._after_album_detail(response)

    def _after_album_detail(self, response):
        """子类覆盖：在专辑所有子请求 yield 后执行（默认无操作）。"""
        pass

    def _make_user_item(self, uid: int, username: str, avatar: str = None) -> UserItem:
        """创建 UserItem，自动处理头像下载。"""
        storage = get_storage_backend()
        avatar_key = storage.upload_image(avatar) if avatar else None
        u = UserItem()
        u["dizzylab_user_id"] = uid
        u["username"] = username
        if avatar_key:
            u["avatar_url"] = avatar_key
        u["user_role"] = "normal"
        return u

    # ── 已购用户 ─────────────────────────────────────

    def parse_buyers(self, response):
        if not check_response_ok(response):
            return
        data = safe_json_load(response)
        if data is None:
            return
        slug = response.meta["_dizzylab_id"]
        names = data.get("names", [])
        user_urls = data.get("user_url", [])
        avatars = data.get("avatar_url", [])

        for i in range(len(names)):
            uid = extract_user_id(user_urls[i]) if i < len(user_urls) else None
            username = names[i]
            avatar = avatars[i].strip('"') if i < len(avatars) else None

            if uid:
                yield self._make_user_item(uid, username, avatar)

            if uid:
                oa = OwnedAlbumItem()
                oa["user_id"] = None
                oa["album_id"] = None
                oa["_dizzylab_user_id"] = uid
                oa["_dizzylab_id"] = slug
                yield oa

    # ── 评论 ─────────────────────────────────────────

    def parse_comments(self, response):
        if not check_response_ok(response):
            return
        data = safe_json_load(response)
        if data is None:
            return
        slug = response.meta["_dizzylab_id"]
        comments = data.get("disc_comment", [])
        user_names = data.get("user_names", [])
        user_urls = data.get("user_url", [])
        avatars = data.get("avatar_url", [])

        for i in range(len(comments)):
            uid = extract_user_id(user_urls[i]) if i < len(user_urls) else None
            username = user_names[i] if i < len(user_names) else None
            avatar = avatars[i].strip('"') if i < len(avatars) else None

            if uid:
                yield self._make_user_item(uid, username, avatar)

            c = CommentItem()
            c["user_id"] = None
            c["album_id"] = None
            c["content"] = comments[i]
            c["created_at"] = datetime.now(timezone.utc)
            c["_dizzylab_user_id"] = uid
            c["_dizzylab_id"] = slug
            yield c

    # ── 社团详情 ─────────────────────────────────────

    def parse_circle_detail(self, response):
        if not check_response_ok(response):
            self.logger.warning("社团详情页异常: %s", response.url)
            return
        labelid = response.meta["_dizzylab_labelid"]
        name = response.meta.get("_labelname", "")

        # 复用共享函数：提取描述和 logo
        description, logo_key = extract_circle_info(response)

        # 复用共享函数：解析成员列表
        member_count = 0
        for item in yield_circle_members(response, labelid):
            yield item
            if isinstance(item, UserCircleItem):
                member_count += 1

        # 更新社团描述、logo、成员数
        self._ensure_db()
        self.repo.update_circle_info_by_labelid(labelid, description, logo_key, member_count)

        if description or member_count > 0:
            self.logger.info("  社团 %s: 描述=%s | 成员=%d",
                           name, "有" if description else "无", member_count)
