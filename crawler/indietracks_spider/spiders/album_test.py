"""
album_test — 测试爬虫：从 API 取 10 张专辑，逐张爬取关联数据。

用法：
    scrapy crawl album_test
"""

import json
import logging
import re
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
from indietracks_spider.utils.delay import between_albums_sleep
from indietracks_spider.utils.config_loader import get_delay_config

logger = logging.getLogger(__name__)

API_DISCS = "https://www.dizzylab.net/apis/getdiscs/"
BASE = "https://www.dizzylab.net"

# 曲目标题解析正则："1. 冬临之时 - Static World (02:48)"
TRACK_RE = re.compile(r"^\d+\.\s*(.+?)\s*\((\d{1,2}:\d{2})\)$")


def extract_user_id(url: str) -> int | None:
    """从 Dizzylab URL 中提取数字 user_id。"""
    m = re.search(r"/u/(\d+)|/albums/u/(\d+)", url)
    return int(m.group(1) or m.group(2)) if m else None


def parse_date_cn(text: str) -> datetime | None:
    """解析"2026年5月1日" → datetime。"""
    m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


class AlbumTestSpider(scrapy.Spider):
    name = "album_test"

    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    def start_requests(self):
        url = f"{API_DISCS}?l=0&r=10&sort=ad&type=album"
        yield scrapy.Request(url, callback=self.parse_disc_list)

    # ── 1. 解析 API 返回的 disc 列表 ──────────────────

    def parse_disc_list(self, response):
        data = json.loads(response.text)
        discs = data.get("discs", [])
        self.logger.info("获取到 %d 张专辑，开始逐张处理", len(discs))

        for disc in discs:
            slug = disc["id"]
            album_url = f"{BASE}/d/{slug}/"

            yield scrapy.Request(
                album_url,
                callback=self.parse_album_detail,
                meta={"disc": disc},
                dont_filter=True,
            )

    # ── 2. 专辑详情页 HTML 解析 ───────────────────────

    def parse_album_detail(self, response):
        disc = response.meta["disc"]
        slug = disc["id"]
        delay_cfg = get_delay_config()

        self.logger.info("[%s] 开始处理: %s", slug, disc.get("title", "?"))

        # ── 2a. 构造 AlbumItem ─────────────────────────
        album = AlbumItem()
        album["dizzylab_id"] = slug
        album["title"] = disc.get("title", "")
        album["price"] = float(disc.get("price", 0))
        album["cover_url"] = disc.get("cover", "")

        # info_title: 所有 <p> 段落拼接
        paragraphs = response.xpath("//p/text()").getall()
        album["info_title"] = "\n".join(p.strip() for p in paragraphs if p.strip())

        # info_content: 所有 <h3> 拼接
        h3s = response.xpath("//h3/text()").getall()
        album["info_content"] = "\n".join(h.strip() for h in h3s if h.strip())

        # publish_date
        pub_text = response.xpath(
            "//text()[contains(., '发布于')]"
        ).get()
        pub_date = parse_date_cn(pub_text) if pub_text else None
        album["publish_date"] = pub_date

        # 封面 data-src（懒加载）
        cover = response.xpath("//img[@id='imgsrc0']/@data-src").get()
        if cover:
            album["cover_url"] = cover

        yield album

        # ── 2b. 曲目列表 ───────────────────────────────
        track_lis = response.xpath("//ul[contains(@class,'playlist--list')]/li")
        for li in track_lis:
            data_id = li.xpath("./@data-id").get()
            data_audio = li.xpath("./@data-audio").get()
            title_text = li.xpath(".//span[@class='t-title']/text()").get()

            wf = WorkFileItem()
            wf["album_id"] = None  # Pipeline 回填
            wf["_dizzylab_id"] = slug  # Pipeline 用此查 album_id
            wf["file_type"] = "preview"
            wf["file_size"] = 0

            if data_id is not None:
                wf["sort_order"] = int(data_id) + 1
            if data_audio:
                wf["object_key"] = data_audio  # 暂存原始 URL

            if title_text:
                m = TRACK_RE.match(title_text.strip())
                if m:
                    wf["file_name"] = m.group(1).strip()
                    wf["track_length"] = m.group(2)
                else:
                    wf["file_name"] = title_text.strip()
                    wf["track_length"] = ""

            yield wf

        # ── 2c. 标签 ───────────────────────────────────
        tag_as = response.xpath("//h4[@class='text-left']/a")
        for a in tag_as:
            raw = a.xpath("./text()").get("")
            # 去掉所有前导 #
            clean = raw.lstrip("#").strip()
            if clean:
                tag = TagItem()
                tag["name"] = clean
                yield tag

                # album_tags 依赖 album_id → Pipeline 内通过 dizzylab_id 缓存关联
                at = AlbumTagItem()
                at["album_id"] = None  # Pipeline 回填
                at["tag_id"] = None    # Pipeline 回填
                # 暂存 tag 名字，Pipeline 里 lookup
                at["_tag_name"] = clean
                at["_dizzylab_id"] = slug
                yield at

        # ── 2d. 社团（API 数据） ───────────────────────
        labelname = disc.get("label", "")
        labelid = disc.get("labelid")
        if labelid:
            circle = CircleItem()
            circle["dizzylab_labelid"] = int(labelid)
            circle["name"] = labelname
            circle["logo_url"] = disc.get("labelcover", "")
            circle["description"] = None  # 从社团详情页补充
            yield circle

            # album_circles
            ac = AlbumCircleItem()
            ac["album_id"] = None
            ac["circle_id"] = None
            ac["_dizzylab_labelid"] = int(labelid)
            ac["_dizzylab_id"] = slug
            yield ac

        # ── 2e. 子请求：已购用户、评论、社团详情 ──────
        buyers_url = (
            f"{BASE}/albums/getbuyers/?discid={slug}&l=0&r=60"
        )
        yield scrapy.Request(
            buyers_url,
            callback=self.parse_buyers,
            meta={"_dizzylab_id": slug},
        )

        comments_url = (
            f"{BASE}/albums/getdisccomment/?discid={slug}&l=0&r=20"
        )
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

    # ── 3. 已购买用户（getbuyers API）─────────────────

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

            # upsert user
            if uid:
                u = UserItem()
                u["dizzylab_user_id"] = uid
                u["username"] = username
                u["avatar_url"] = avatar
                u["user_role"] = "normal"
                yield u

            # owned_albums
            if uid:
                oa = OwnedAlbumItem()
                oa["user_id"] = None
                oa["album_id"] = None
                oa["_dizzylab_user_id"] = uid
                oa["_dizzylab_id"] = slug
                yield oa

    # ── 4. 评论（getdisccomment API）──────────────────

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
            c["user_id"] = None     # Pipeline 回填
            c["album_id"] = None    # Pipeline 回填
            c["content"] = comments[i]
            c["created_at"] = datetime.now()
            c["_dizzylab_user_id"] = uid
            c["_dizzylab_id"] = slug
            yield c

    # ── 5. 社团详情页 ─────────────────────────────────

    def parse_circle_detail(self, response):
        labelid = response.meta["_dizzylab_labelid"]

        # 成员列表
        member_as = response.xpath(
            "//p[text()='成员']/following-sibling::div//a[contains(@href,'/u/')]"
        )
        for a in member_as:
            href = a.xpath("./@href").get("")
            uid = extract_user_id(href)
            # 从 title 属性提取用户名
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
