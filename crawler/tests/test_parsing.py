"""utils/parsing.py 单元测试。"""

import pytest
from datetime import datetime

from indietracks_spider.utils.parsing import (
    extract_user_id,
    parse_date_cn,
    parse_track_title,
    safe_json_load,
    check_response_ok,
)


# ── extract_user_id ─────────────────────────────────

class TestExtractUserId:
    def test_standard_url(self):
        assert extract_user_id("/u/12345") == 12345

    def test_album_url(self):
        assert extract_user_id("/albums/u/90162") == 90162

    def test_full_url(self):
        assert extract_user_id("https://www.dizzylab.net/u/4725") == 4725

    def test_no_match(self):
        assert extract_user_id("/d/SomeAlbum") is None

    def test_empty_string(self):
        assert extract_user_id("") is None


# ── parse_date_cn ───────────────────────────────────

class TestParseDateCn:
    def test_standard_date(self):
        result = parse_date_cn("发布于2026年5月1日")
        assert result == datetime(2026, 5, 1)

    def test_single_digit_month(self):
        result = parse_date_cn("发布于2025年1月18日")
        assert result == datetime(2025, 1, 18)

    def test_no_match(self):
        assert parse_date_cn("no date here") is None

    def test_none_input(self):
        assert parse_date_cn(None) is None


# ── parse_track_title ───────────────────────────────

class TestParseTrackTitle:
    def test_standard_track(self):
        name, length = parse_track_title("1. 冬临之时 - Static World (02:48)")
        assert name == "冬临之时 - Static World"
        assert length == "02:48"

    def test_single_digit_number(self):
        name, length = parse_track_title("9. Some Track (03:15)")
        assert name == "Some Track"
        assert length == "03:15"

    def test_no_match(self):
        name, length = parse_track_title("No number prefix")
        assert name == "No number prefix"
        assert length == ""

    def test_empty_string(self):
        name, length = parse_track_title("")
        assert name == ""
        assert length == ""


# ── safe_json_load ──────────────────────────────────

class TestSafeJsonLoad:
    def test_valid_json(self, mocker):
        response = mocker.Mock()
        response.text = '{"key": "value"}'
        result = safe_json_load(response)
        assert result == {"key": "value"}

    def test_invalid_json(self, mocker):
        response = mocker.Mock()
        response.text = 'not json'
        result = safe_json_load(response)
        assert result is None

    def test_empty_response(self, mocker):
        response = mocker.Mock()
        response.text = ''
        result = safe_json_load(response)
        assert result is None


# ── check_response_ok ───────────────────────────────

class TestCheckResponseOk:
    def test_200(self, mocker):
        response = mocker.Mock()
        response.status = 200
        assert check_response_ok(response) is True

    def test_301_redirect_ok(self, mocker):
        """3xx 重定向不阻断（Scrapy 已处理）。"""
        response = mocker.Mock()
        response.status = 301
        response.url = "http://example.com"
        assert check_response_ok(response) is True

    def test_404(self, mocker):
        response = mocker.Mock()
        response.status = 404
        response.url = "http://example.com"
        assert check_response_ok(response) is False

    def test_429_rate_limit(self, mocker):
        """429 应返回 False，由 Scrapy retry 处理。"""
        response = mocker.Mock()
        response.status = 429
        response.url = "http://example.com"
        assert check_response_ok(response) is False

    def test_500(self, mocker):
        response = mocker.Mock()
        response.status = 500
        response.url = "http://example.com"
        assert check_response_ok(response) is False
