"""
BaseAlbumSpider — 专辑爬虫基类。

提取 album_bulk / album_incremental / album_test 共享的解析方法：
- parse_album_detail（含 MinIO 音频下载）
- parse_buyers / parse_comments / parse_circle_detail
- _album_is_complete / _ensure_db_check
"""

import json
import logging
from datetime import datetime
from urllib.parse import quote

import scrapy

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
from indietracks_spider.utils.constants import BASE, TRACK_RE
from indietracks_spider.utils.db import get_connection
from indietracks_spider.utils.delay import between_tracks_sleep
from indietracks_spider.utils.minio import download_and_upload
from indietracks_spider.utils.parsing import (
    extract_user_id,
    parse_date_cn,
    safe_json_load,
    check_response_ok,
)

logger = logging.getLogger(__name__)


class BaseAlbumSpider(scrapy.Spider):
    """专辑爬虫基类——子类只需实现 start_requests 和 parse_disc_list。"""

    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    # ── 子类可覆盖的属性 ──────────────────────────────

    _track_min: int = 1
    _track_random_max: int = 3
    _check_conn = None
    _check_cur = None

    # ── DB 检查 ──────────────────────────────────────

    def _ensure_db_check(self):
        if self._check_cur is not None:
            return
        self._check_conn, self._check_cur = get_connection()

    def _album_is_complete(self, dizzylab_id: str) -> bool:
        self._ensure_db_check()
        self._check_cur.execute(
            "SELECT info_title FROM albums WHERE dizzylab_id = %s",
            (dizzylab_id,),
        )
        row = self._check_cur.fetchone()
        return row is not None and row[0] is not None

    def _close_check_db(self):
        if self._check_cur:
            self._check_cur.close()
        if self._check_conn:
            self._check_conn.close()

    def closed(self, reason):
        self._close_check_db()

    # ── 专辑详情页 ───────────────────────────────────

    def parse_album_detail(self, response):
        disc = response.meta["disc"]
        slug = disc["id"]

        # ── AlbumItem ──
        album = AlbumItem()
        album["dizzylab_id"] = slug
        album["title"] = disc.get("title", "")
        album["price"] = float(disc.get("price", 0))
        album["cover_url"] = disc.get("cover", "")

        paragraphs = response.xpath("//p/text()").getall()
        album["info_title"] = "\n".join(p.strip() for p in paragraphs if p.strip())

        h3s = response.xpath("//h3/text()").getall()
        album["info_content"] = "\n".join(h.strip() for h in h3s if h.strip())

        pub_text = response.xpath("//text()[contains(., '发布于')]").get()
        pub_date = parse_date_cn(pub_text) if pub_text else None
        album["publish_date"] = pub_date

        cover = response.xpath("//img[@id='imgsrc0']/@data-src").get()
        if cover:
            album["cover_url"] = cover

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
                result = download_and_upload(data_audio, slug, sort_order)
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
                m = TRACK_RE.match(title_text.strip())
                if m:
                    wf["file_name"] = m.group(1).strip()
                    wf["track_length"] = m.group(2)
                else:
                    wf["file_name"] = title_text.strip()
                    wf["track_length"] = ""

            yield wf

            between_tracks_sleep(self._track_min, self._track_random_max)

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
            circle["logo_url"] = disc.get("labelcover", "")
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
                u = UserItem()
                u["dizzylab_user_id"] = uid
                u["username"] = username
                u["avatar_url"] = avatar
                u["user_role"] = "normal"
                yield u

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

        for i in range(len(comments)):
            uid = extract_user_id(user_urls[i]) if i < len(user_urls) else None
            username = user_names[i] if i < len(user_names) else None

            if uid:
                u = UserItem()
                u["dizzylab_user_id"] = uid
                u["username"] = username
                u["user_role"] = "normal"
                yield u

            c = CommentItem()
            c["user_id"] = None
            c["album_id"] = None
            c["content"] = comments[i]
            c["created_at"] = datetime.now()
            c["_dizzylab_user_id"] = uid
            c["_dizzylab_id"] = slug
            yield c

    # ── 社团详情 ─────────────────────────────────────

    def parse_circle_detail(self, response):
        labelid = response.meta["_dizzylab_labelid"]

        member_as = response.xpath(
            "//p[text()='成员']/following-sibling::div//a[contains(@href,'/u/')]"
        )
        for a in member_as:
            href = a.xpath("./@href").get("")
            uid = extract_user_id(href)
            title = a.xpath("./@title").get("")
            username = None
            if title:
                br_pos = title.rfind("<br>")
                if br_pos != -1:
                    username = title[br_pos + 4:].strip()
                else:
                    username = title.strip()

            if uid:
                u = UserItem()
                u["dizzylab_user_id"] = uid
                u["username"] = username
                u["user_role"] = "normal"
                yield u

                uc = UserCircleItem()
                uc["user_id"] = None
                uc["circle_id"] = None
                uc["_dizzylab_user_id"] = uid
                uc["_dizzylab_labelid"] = labelid
                yield uc
