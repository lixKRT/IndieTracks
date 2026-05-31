"""utils/constants.py 单元测试。"""

import re
from indietracks_spider.utils.constants import BASE, API_DISCS, PAGE_SIZE, TRACK_RE


class TestConstants:
    def test_base_url(self):
        assert BASE == "https://www.dizzylab.net"

    def test_api_discs(self):
        assert API_DISCS == "https://www.dizzylab.net/apis/getdiscs/"

    def test_page_size(self):
        assert PAGE_SIZE == 24

    def test_track_re_valid(self):
        match = TRACK_RE.match("1. 冬临之时 - Static World (02:48)")
        assert match is not None
        assert match.group(1) == "冬临之时 - Static World"
        assert match.group(2) == "02:48"

    def test_track_re_no_match(self):
        assert TRACK_RE.match("no match") is None

    def test_track_re_single_digit(self):
        match = TRACK_RE.match("9. Track Name (03:15)")
        assert match is not None
        assert match.group(1) == "Track Name"
        assert match.group(2) == "03:15"
