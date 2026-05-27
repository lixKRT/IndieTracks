"""
user_roles — 用户角色爬虫

爬取 /setup 页，解析 STAFF 和 PRO 用户列表，写入 users.user_role。
遵守 spider.json 的 mode 控制。

用法：
    scrapy crawl user_roles
"""

import logging

import scrapy
from scrapy.exceptions import CloseSpider

from indietracks_spider.utils.config_loader import get_spider_config
from indietracks_spider.utils.constants import BASE
from indietracks_spider.utils.db import get_connection, close_connection
from indietracks_spider.utils.parsing import extract_user_id, check_response_ok

logger = logging.getLogger(__name__)


class UserRolesSpider(scrapy.Spider):
    name = "user_roles"

    custom_settings = {
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        spider_cfg = get_spider_config()
        self._mode = spider_cfg.get("mode", "full")

        self._db_conn = None
        self._db_cur = None
        self._staff_count = 0
        self._pro_count = 0
        self._skipped_count = 0

        self.logger.info("user_roles 启动 | mode=%s", self._mode)

    def _ensure_db(self):
        if self._db_cur is not None:
            return
        self._db_conn, self._db_cur = get_connection()

    def _update_role(self, dizzylab_user_id: int, role: str) -> bool:
        """更新用户角色。incremental 模式跳过已有 role 的用户。"""
        self._ensure_db()

        if self._mode == "incremental":
            self._db_cur.execute(
                "SELECT user_role FROM users WHERE dizzylab_user_id = %s",
                (dizzylab_user_id,),
            )
            row = self._db_cur.fetchone()
            if row and row[0] and row[0] != "normal":
                self._skipped_count += 1
                return False

        self._db_cur.execute(
            """INSERT INTO users (dizzylab_user_id, username, user_role)
               VALUES (%s, %s, %s)
               ON CONFLICT (dizzylab_user_id) DO UPDATE
                 SET user_role = EXCLUDED.user_role""",
            (dizzylab_user_id, f"user_{dizzylab_user_id}", role),
        )
        return True

    def closed(self, reason):
        close_connection(self._db_conn, self._db_cur)
        self.logger.info(
            "user_roles 结束 | staff=%d | pro=%d | skipped=%d | mode=%s | reason=%s",
            self._staff_count,
            self._pro_count,
            self._skipped_count,
            self._mode,
            reason,
        )

    # ── 入口 ─────────────────────────────────────────

    def start_requests(self):
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

        # PRO 用户
        pro_heading = response.xpath("//h2[contains(., 'PRO')]")
        if pro_heading:
            pro_links = pro_heading[0].xpath(
                "./following-sibling::a[contains(@href, '/u/')]"
            )
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
