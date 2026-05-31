"""album_base.py 单元测试 — 工具方法。"""

from __future__ import annotations

import json
import pytest
from unittest.mock import MagicMock

from indietracks_spider.spiders.album_base import BaseAlbumSpider
from indietracks_spider.utils.constants import API_DISCS, PAGE_SIZE


class TestMakeDiscRequest:
    def test_constructs_correct_url(self):
        req = BaseAlbumSpider.make_disc_request(0, MagicMock())
        assert f"{API_DISCS}?l=0&r={PAGE_SIZE}&sort=ad&type=album" == req.url

    def test_page_offset(self):
        req = BaseAlbumSpider.make_disc_request(48, MagicMock())
        assert "l=48" in req.url
        assert f"r={48 + PAGE_SIZE}" in req.url

    def test_callback_set(self):
        cb = MagicMock()
        req = BaseAlbumSpider.make_disc_request(0, cb)
        assert req.callback is cb

    def test_meta_passed(self):
        req = BaseAlbumSpider.make_disc_request(0, MagicMock(), meta={"page_start": 0})
        assert req.meta["page_start"] == 0

    def test_dont_filter(self):
        req = BaseAlbumSpider.make_disc_request(0, MagicMock())
        assert req.dont_filter is True


class TestParseDiscsResponse:
    def _make_response(self, data=None, status=200):
        from scrapy.http import TextResponse
        body = json.dumps(data or {}).encode("utf-8")
        return TextResponse(url="https://example.com", body=body, encoding="utf-8", status=status)

    def test_valid_response(self):
        response = self._make_response({"discs": [{"id": "SW20"}, {"id": "SW21"}]})
        result = BaseAlbumSpider._parse_discs_response(response)
        assert result is not None
        assert len(result) == 2
        assert result[0]["id"] == "SW20"

    def test_empty_discs(self):
        response = self._make_response({"discs": []})
        result = BaseAlbumSpider._parse_discs_response(response)
        assert result is not None
        assert len(result) == 0

    def test_missing_discs_key(self):
        response = self._make_response({"other": "data"})
        result = BaseAlbumSpider._parse_discs_response(response)
        assert result is not None
        assert len(result) == 0

    def test_http_error(self):
        response = self._make_response(status=404)
        result = BaseAlbumSpider._parse_discs_response(response)
        assert result is None

    def test_invalid_json(self):
        from scrapy.http import TextResponse
        response = TextResponse(url="https://example.com", body=b"not json", encoding="utf-8")
        result = BaseAlbumSpider._parse_discs_response(response)
        assert result is None
