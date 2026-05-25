"""
album_bulk — 批量爬虫

用途：首次数据铺底 + 全量刷新。遵守 spider.json 的 mode / max_albums 控制。

用法：
    scrapy crawl album_bulk
"""

import json
import logging
import random
import re
import time
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
from indietracks_spider.utils.config_loader import (
    get_delay_config,
    get_database_config,
    get_spider_config,
)
from indietracks_spider.utils.minio import download_and_upload

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


class AlbumBulkSpider(scrapy.Spider):
    name = "album_bulk"

    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        spider_cfg = get_spider_config()
        self._mode = spider_cfg.get("mode", "full")
        self._max_albums = spider_cfg.get("max_albums", 0)

        delay_cfg = get_delay_config()
        self._between_min = delay_cfg.get("between_albums_min", 60)
        self._between_random = delay_cfg.get("between_albums_random", 60)
        self._track_min = delay_cfg.get("between_tracks_min", 1)
        self._track_random_max = delay_cfg.get("between_tracks_random_max", 5)

        self._processed = 0
        self._skipped = 0
        self._check_conn = None
        self._check_cur = None

        self.logger.info(
            "album_bulk 启动 | mode=%s | max_albums=%s | between=%d+rand(0,%d)s",
            self._mode,
            self._max_albums if self._max_albums > 0 else "∞",
            self._between_min,
            self._between_random,
        )

    def _ensure_db_check(self):
        """延迟初始化数据库查询连接（避免 spider 构造时连库失败导致崩溃）。"""
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

    def _album_is_complete(self, dizzylab_id: str) -> bool:
        """专辑是否已存在且数据完整（info_title 非空）。"""
        self._ensure_db_check()
        self._check_cur.execute(
            "SELECT info_title FROM albums WHERE dizzylab_id = %s",
            (dizzylab_id,),
        )
        row = self._check_cur.fetchone()
        return row is not None and row[0] is not None

    def closed(self, reason):
        if self._check_cur:
            self._check_cur.close()
        if self._check_conn:
            self._check_conn.close()
        self.logger.info(
            "album_bulk 结束 | processed=%d | skipped=%d | reason=%s",
            self._processed,
            self._skipped,
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
            self.logger.info("API 返回 0 条数据，翻页结束")
            raise CloseSpider("数据源已耗尽")

        self.logger.info("翻页 l=%d，获取到 %d 张专辑", page_start, len(discs))

        for disc in discs:
            # 达到限额则停止（break 保证已 yield 的请求能处理完）
            if self._max_albums > 0 and self._processed >= self._max_albums:
                self.logger.info("已达上限 %d 张，停止翻页", self._max_albums)
                return

            slug = disc["id"]
            complete = self._album_is_complete(slug)

            # incremental 模式：仅跳过数据完整的专辑
            if self._mode == "incremental" and complete:
                self._skipped += 1
                self.logger.info(
                    "[%s] 跳过 | 数据完整 | 累计跳过: %d",
                    slug,
                    self._skipped,
                )
                continue

            # 处理此专辑
            self._processed += 1
            max_str = str(self._max_albums) if self._max_albums > 0 else "∞"

            self.logger.info(
                "[%d/%s] %s - %s ✓ | mode=%s | 跳过: %d",
                self._processed,
                max_str,
                slug,
                disc.get("title", "?"),
                self._mode,
                self._skipped,
            )

            album_url = f"{BASE}/d/{slug}/"
            yield scrapy.Request(
                album_url,
                callback=self.parse_album_detail,
                meta={"disc": disc},
                dont_filter=True,
            )

        # 翻到下一页（还有限额或无限额）
        if self._max_albums == 0 or self._processed < self._max_albums:
            next_start = page_start + PAGE_SIZE
            next_r = next_start + PAGE_SIZE
            next_url = f"{API_DISCS}?l={next_start}&r={next_r}&sort=ad&type=album"
            yield scrapy.Request(
                next_url,
                callback=self.parse_disc_list,
                meta={"page_start": next_start},
                dont_filter=True,
            )

    # ── 2. 专辑详情页  ──────────────────────────────

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
                    continue  # 跳过该曲目

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

            # 曲目间延迟
            delay = self._track_min + random.randint(0, self._track_random_max)
            if delay > 0:
                time.sleep(delay)

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

        # 专辑间延迟（在子请求 yield 后，下一张 detail 页触发前）
        if self._max_albums == 0 or self._processed < self._max_albums:
            wait = self._between_min + random.randint(0, self._between_random)
            self.logger.info("专辑间延迟 %ds（min=%d + rand(%d)）", wait, self._between_min, self._between_random)
            time.sleep(wait)

    # ── 3. 已购买用户 ────────────────────────────────

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

    # ── 4. 评论 ─────────────────────────────────────

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

    # ── 5. 社团详情 ─────────────────────────────────

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
