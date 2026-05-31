"""社团详情页解析 — 共享函数。

从社团详情页 HTML 中提取描述、logo、成员列表。
供 circle.py 爬虫和 album_base.py 复用。
"""

import logging

from indietracks_spider.items import UserItem, UserCircleItem
from indietracks_spider.utils.minio import download_image
from indietracks_spider.utils.parsing import extract_user_id

logger = logging.getLogger(__name__)


def extract_circle_info(response):
    """提取社团描述和 logo（不 yield item）。

    Returns: (description, logo_key)
    """
    description = response.xpath("//p[@id='labeldesp']/text()").get("").strip()
    logo_url = response.xpath(
        "//img[@id='imgsrc0' or contains(@data-src,'label_cover')]/@data-src"
    ).get("")
    logo_key = download_image(logo_url) if logo_url else None
    return description, logo_key


def yield_circle_members(response, labelid: int):
    """解析社团成员列表，yield UserItem + UserCircleItem。

    Returns: member_count
    """
    member_as = response.xpath(
        "//p[text()='成员']/following-sibling::div//a[contains(@href,'/u/')]"
    )

    found = 0
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
            u["user_role"] = "pro"
            yield u

            uc = UserCircleItem()
            uc["user_id"] = None
            uc["circle_id"] = None
            uc["_dizzylab_user_id"] = uid
            uc["_dizzylab_labelid"] = labelid
            yield uc
            found += 1

    return found
