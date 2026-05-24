"""
album_incremental — 增量爬虫

永远增量，不受 spider.json 控制。从 API 最新页开始翻，遇到第一条
数据库中已存在的 dizzylab_id 立即停止。

用法：
    scrapy crawl album_incremental
"""

import json
import logging
import re
from datetime import datetime
from urllib.parse import quote

import psycopg2
import scrapy
from scrapy.exceptions import CloseSpider

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
from indietracks_spider.utils.config_loader import get_database_config

logger = logging.getLogger(__name__)

API_DISCS = "https://www.dizzylab.net/apis/getdiscs/"
BASE = "https://www.dizzylab.net"
PAGE_SIZE = 24

TRACK_RE = re.compile(r"^\d+\.\s*(.+?)\s*\((\d{1,2}:\d{2})\)$")


def extract_user_id(url: str) -> int | None:
    m = re.search(r"/u/(\d+)|/albums/u/(\d+)", url)
    return int(m.group(1) or m.group(2)) if m else None


def parse_date_cn(text: str) -> datetime | None:
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


class AlbumIncrementalSpider(scrapy.Spider):
    name = "album_incremental"

    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._captured = 0
        self._check_conn = None
        self._check_cur = None
        self.logger.info("album_incremental 启动 | 永远增量模式 | 遇到已存在即停")

    def _ensure_db_check(self):
        if self._check_cur is not None:
            return
        db = get_database_config()
        if not db.get("user"):
            raise RuntimeError("数据库未配置，请编辑 crawler/config/database.json")
        self._check_conn = psycopg2.connect(
            host=db["host"],
            port=db["port"],
            database=db["database"],
            user=db["user"],
            password=db["password"],
            options="-c client_encoding=UTF8",
        )
        self._check_conn.autocommit = True
        self._check_cur = self._check_conn.cursor()

    def _album_exists(self, dizzylab_id: str) -> bool:
        self._ensure_db_check()
        self._check_cur.execute(
            "SELECT EXISTS(SELECT 1 FROM albums WHERE dizzylab_id = %s)",
            (dizzylab_id,),
        )
        return self._check_cur.fetchone()[0]

    def closed(self, reason):
        if self._check_cur:
            self._check_cur.close()
        if self._check_conn:
            self._check_conn.close()
        self.logger.info(
            "album_incremental 结束 | captured=%d | reason=%s",
            self._captured,
            reason,
        )

    # ── 入口 ─────────────────────────────────────────

    def start_requests(self):
        url = f"{API_DISCS}?l=0&r={PAGE_SIZE}&sort=ad&type=album"
        yield scrapy.Request(
            url,
            callback=self.parse_disc_list,
            meta={"page_start": 0},
            dont_filter=True,
        )

    # ── 1. 翻页处理 ─────────────────────────────────

    def parse_disc_list(self, response):
        page_start = response.meta["page_start"]
        data = json.loads(response.text)
        discs = data.get("discs", [])

        if not discs:
            self.logger.info("API 返回 0 条，停止")
            raise CloseSpider("数据源已耗尽")

        self.logger.info("翻页 l=%d，获取到 %d 张专辑", page_start, len(discs))

        for disc in discs:
            slug = disc["id"]

            if self._album_exists(slug):
                self.logger.info("遇到已存在专辑 %s，停止", slug)
                raise CloseSpider(f"已追平最新数据（{slug} 已存在）")

            self._captured += 1
            self.logger.info(
                "[%d] %s - %s",
                self._captured,
                slug,
                disc.get("title", "?"),
            )

            album_url = f"{BASE}/d/{slug}/"
            yield scrapy.Request(
                album_url,
                callback=self.parse_album_detail,
                meta={"disc": disc},
                dont_filter=True,
            )

        # 当前页全是新专辑，翻下一页
        next_start = page_start + PAGE_SIZE
        next_r = next_start + PAGE_SIZE
        next_url = f"{API_DISCS}?l={next_start}&r={next_r}&sort=ad&type=album"
        yield scrapy.Request(
            next_url,
            callback=self.parse_disc_list,
            meta={"page_start": next_start},
            dont_filter=True,
        )

    # ── 以下 parse_* 方法与 album_bulk 一致 ──────────

    def parse_album_detail(self, response):
        disc = response.meta["disc"]
        slug = disc["id"]

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

        track_lis = response.xpath("//ul[contains(@class,'playlist--list')]/li")
        for li in track_lis:
            data_id = li.xpath("./@data-id").get()
            data_audio = li.xpath("./@data-audio").get()
            title_text = li.xpath(".//span[@class='t-title']/text()").get()

            wf = WorkFileItem()
            wf["album_id"] = None
            wf["_dizzylab_id"] = slug
            wf["file_type"] = "preview"
            wf["file_size"] = 0

            if data_id is not None:
                wf["sort_order"] = int(data_id) + 1
            if data_audio:
                wf["object_key"] = data_audio

            if title_text:
                m = TRACK_RE.match(title_text.strip())
                if m:
                    wf["file_name"] = m.group(1).strip()
                    wf["track_length"] = m.group(2)
                else:
                    wf["file_name"] = title_text.strip()
                    wf["track_length"] = ""

            yield wf

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

        buyers_url = f"{BASE}/albums/getbuyers/?discid={slug}&l=0&r=60"
        yield scrapy.Request(
            buyers_url,
            callback=self.parse_buyers,
            meta={"_dizzylab_id": slug},
        )

        comments_url = f"{BASE}/albums/getdisccomment/?discid={slug}&l=0&r=20"
        yield scrapy.Request(
            comments_url,
            callback=self.parse_comments,
            meta={"_dizzylab_id": slug},
        )

        if labelname:
            circle_url = f"{BASE}/l/{quote(labelname)}/"
            yield scrapy.Request(
                circle_url,
                callback=self.parse_circle_detail,
                meta={
                    "_dizzylab_labelid": int(labelid) if labelid else None,
                    "_labelname": labelname,
                },
            )

    def parse_buyers(self, response):
        slug = response.meta["_dizzylab_id"]
        data = json.loads(response.text)
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

    def parse_comments(self, response):
        slug = response.meta["_dizzylab_id"]
        data = json.loads(response.text)
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
