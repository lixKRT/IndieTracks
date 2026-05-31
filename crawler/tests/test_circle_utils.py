"""utils/circle.py 单元测试。"""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from indietracks_spider.utils.circle import extract_circle_info, yield_circle_members
from indietracks_spider.items import UserItem, UserCircleItem


def _make_selector_list(items):
    """创建模拟 Scrapy SelectorList 的对象。

    SelectorList 有 .get(default) 方法返回第一个元素的文本。
    """
    mock_list = MagicMock()
    mock_list.get.return_value = items[0] if items else ""
    mock_list.__iter__ = MagicMock(return_value=iter(items))
    mock_list.__len__ = MagicMock(return_value=len(items))
    mock_list.__bool__ = MagicMock(return_value=len(items) > 0)
    return mock_list


class TestExtractCircleInfo:
    @patch("indietracks_spider.utils.circle.get_storage_backend")
    def test_extracts_description_and_logo(self, mock_get_storage):
        mock_storage = MagicMock()
        mock_storage.upload_image.return_value = "logos/test.jpg"
        mock_get_storage.return_value = mock_storage

        response = MagicMock()

        def xpath_side_effect(sel):
            if "labeldesp" in sel:
                return _make_selector_list(["Test description"])
            if "imgsrc0" in sel or "label_cover" in sel:
                return _make_selector_list(["https://cdn.dizzylab.net/media/label_cover/logo.jpg"])
            return _make_selector_list([])

        response.xpath.side_effect = xpath_side_effect

        desc, logo = extract_circle_info(response)
        assert desc == "Test description"
        assert logo == "logos/test.jpg"
        mock_storage.upload_image.assert_called_once_with("https://cdn.dizzylab.net/media/label_cover/logo.jpg")

    @patch("indietracks_spider.utils.circle.get_storage_backend")
    def test_empty_description_no_logo(self, mock_get_storage):
        mock_storage = MagicMock()
        mock_get_storage.return_value = mock_storage

        response = MagicMock()

        def xpath_side_effect(sel):
            return _make_selector_list([""])

        response.xpath.side_effect = xpath_side_effect

        desc, logo = extract_circle_info(response)
        assert desc == ""
        assert logo is None
        mock_storage.upload_image.assert_not_called()


class TestYieldCircleMembers:
    @patch("indietracks_spider.utils.circle.get_storage_backend")
    def test_yields_user_and_circle_items(self, mock_get_storage):
        response = MagicMock()

        mock_href = MagicMock()
        mock_href.get.return_value = "/u/12345"
        mock_title = MagicMock()
        mock_title.get.return_value = "TestUser<br>DisplayName"

        mock_a = MagicMock()
        mock_a.xpath.side_effect = lambda sel: {
            "./@href": mock_href,
            "./@title": mock_title,
        }.get(sel, MagicMock(get=MagicMock(return_value="")))

        def xpath_side_effect(sel):
            if "成员" in sel:
                mock_list = MagicMock()
                mock_list.__iter__ = MagicMock(return_value=iter([mock_a]))
                return mock_list
            return _make_selector_list([])

        response.xpath.side_effect = xpath_side_effect

        items = list(yield_circle_members(response, 30))
        assert len(items) == 2
        assert isinstance(items[0], UserItem)
        assert items[0]["dizzylab_user_id"] == 12345
        assert items[0]["username"] == "DisplayName"
        assert isinstance(items[1], UserCircleItem)
        assert items[1]["_dizzylab_user_id"] == 12345
        assert items[1]["_dizzylab_labelid"] == 30

    @patch("indietracks_spider.utils.circle.get_storage_backend")
    def test_no_members(self, mock_get_storage):
        response = MagicMock()
        response.xpath.return_value = _make_selector_list([])

        items = list(yield_circle_members(response, 30))
        assert len(items) == 0

    @patch("indietracks_spider.utils.circle.get_storage_backend")
    def test_member_without_uid_skipped(self, mock_get_storage):
        response = MagicMock()

        mock_href = MagicMock()
        mock_href.get.return_value = "/d/something"
        mock_title = MagicMock()
        mock_title.get.return_value = "NoUser"

        mock_a = MagicMock()
        mock_a.xpath.side_effect = lambda sel: {
            "./@href": mock_href,
            "./@title": mock_title,
        }.get(sel, MagicMock(get=MagicMock(return_value="")))

        def xpath_side_effect(sel):
            if "成员" in sel:
                mock_list = MagicMock()
                mock_list.__iter__ = MagicMock(return_value=iter([mock_a]))
                return mock_list
            return _make_selector_list([])

        response.xpath.side_effect = xpath_side_effect

        items = list(yield_circle_members(response, 30))
        assert len(items) == 0

    @patch("indietracks_spider.utils.circle.get_storage_backend")
    def test_multiple_members(self, mock_get_storage):
        response = MagicMock()

        def make_a(href, title):
            mock_href = MagicMock()
            mock_href.get.return_value = href
            mock_title = MagicMock()
            mock_title.get.return_value = title
            mock_a = MagicMock()
            mock_a.xpath.side_effect = lambda sel, h=mock_href, t=mock_title: {
                "./@href": h, "./@title": t,
            }.get(sel, MagicMock(get=MagicMock(return_value="")))
            return mock_a

        members = [
            make_a("/u/1", "User1"),
            make_a("/u/2", "User2<br>Name2"),
            make_a("/u/3", "User3"),
        ]

        def xpath_side_effect(sel):
            if "成员" in sel:
                mock_list = MagicMock()
                mock_list.__iter__ = MagicMock(return_value=iter(members))
                return mock_list
            return _make_selector_list([])

        response.xpath.side_effect = xpath_side_effect

        items = list(yield_circle_members(response, 30))
        assert len(items) == 6
        assert items[0]["dizzylab_user_id"] == 1
        assert items[2]["dizzylab_user_id"] == 2
        assert items[2]["username"] == "Name2"
        assert items[4]["dizzylab_user_id"] == 3
