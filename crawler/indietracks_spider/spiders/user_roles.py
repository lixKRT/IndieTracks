"""
user_roles — 用户角色爬虫

爬取 /setup 页，解析 STAFF 和 PRO 用户列表，写入 users.user_role。
遵守 spider.json 的 mode 控制。

用法：
    scrapy crawl user_roles
"""

from __future__ import annotations

import logging

import scrapy
from scrapy.exceptions import CloseSpider

from indietracks_spider.db_mixin import DbSpiderMixin
from indietracks_spider.utils.config_loader import get_spider_config
from indietracks_spider.utils.constants import BASE
from indietracks_spider.utils.parsing import extract_user_id, check_response_ok

logger = logging.getLogger(__name__)


class UserRolesSpider(DbSpiderMixin, scrapy.Spider):
    name = "user_roles"

    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        spider_cfg = get_spider_config()
        self._mode = spider_cfg.get("mode", "full")

        self._staff_count = 0
        self._pro_count = 0
        self._skipped_count = 0

        self.logger.info("user_roles 启动 | mode=%s", self._mode)

    def _update_role(self, dizzylab_user_id: int, role: str) -> bool:
        """更新用户角色。incremental 模式跳过已有 role 的用户。"""
        self._ensure_db()

        if self._mode == "incremental":
            wrote = self.repo.update_role_if_normal(dizzylab_user_id, role)
            if not wrote:
                self._skipped_count += 1
                return False
            return True
        else:
            self.repo.update_role(dizzylab_user_id, role)
            return True

    def closed(self, reason):
        super().closed(reason)
        self.logger.info(
            "user_roles 结束 | staff=%d | pro=%d | skipped=%d | mode=%s | reason=%s",
            self._staff_count,
            self._pro_count,
            self._skipped_count,
            self._mode,
            reason,
        )

    # ── 入口 ─────────────────────────────────────────

    async def start(self):
        yield scrapy.Request(
            f"{BASE}/setup",
            callback=self.parse_setup,
            dont_filter=True,
        )

    # ── 解析 /setup ─────────────────────────────────

    def parse_setup(self, response):
        if not check_response_ok(response):
            self.logger.error("setup 页面访问失败，无法获取角色数据")
            raise CloseSpider("setup 页面异常")
        # STAFF 用户（仅取 STAFF h2 和 PRO h2 之间的链接）
        staff_heading = response.xpath("//h2[contains(., 'STAFF')]")
        if staff_heading:
            staff_links = staff_heading[0].xpath(
                "./following-sibling::a[contains(@href, '/u/')]"
                "[not(preceding-sibling::h2[contains(., 'PRO')])]"
            )
            for a in staff_links:
                href = a.xpath("./@href").get("")
                uid = extract_user_id(href)
                if uid and self._update_role(uid, "staff"):
                    self._staff_count += 1
            self.logger.info("STAFF: 找到 %d 人，实际写入 %d", len(staff_links), self._staff_count)

        # PRO 用户（到下一个 h2 为止，避免溢出到后续区域）
        pro_heading = response.xpath("//h2[contains(., 'PRO')]")
        if pro_heading:
            # 取 PRO h2 之后的所有兄弟节点，遇到下一个 h2 就停
            pro_links = []
            for sibling in pro_heading[0].xpath("./following-sibling::*"):
                tag = sibling.xpath("name()").get("")
                if tag == "h2":
                    break
                if tag == "a" and "/u/" in (sibling.xpath("./@href").get("")):
                    pro_links.append(sibling)
            for a in pro_links:
                href = a.xpath("./@href").get("")
                uid = extract_user_id(href)
                if uid and self._update_role(uid, "pro"):
                    self._pro_count += 1
            self.logger.info("PRO: 找到 %d 人，实际写入 %d", len(pro_links), self._pro_count)

        self.logger.info(
            "写入完成 | staff=%d | pro=%d | skipped=%d",
            self._staff_count,
            self._pro_count,
            self._skipped_count,
        )
        raise CloseSpider("user_roles 完成")
