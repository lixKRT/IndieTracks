"""utils/delay.py 单元测试。"""

from __future__ import annotations

from unittest.mock import patch, MagicMock
import pytest


class TestScheduleAlbumDelay:
    @patch("indietracks_spider.utils.delay._get_reactor")
    @patch("indietracks_spider.utils.delay.random")
    def test_calls_reactor_calllater(self, mock_random, mock_get_reactor):
        mock_random.randint.return_value = 5
        mock_reactor = MagicMock()
        mock_get_reactor.return_value = mock_reactor

        from indietracks_spider.utils.delay import schedule_album_delay
        callback = MagicMock()
        schedule_album_delay(60, 10, callback)
        mock_reactor.callLater.assert_called_once_with(65, callback)

    @patch("indietracks_spider.utils.delay._get_reactor")
    @patch("indietracks_spider.utils.delay.random")
    def test_min_only(self, mock_random, mock_get_reactor):
        mock_random.randint.return_value = 0
        mock_reactor = MagicMock()
        mock_get_reactor.return_value = mock_reactor

        from indietracks_spider.utils.delay import schedule_album_delay
        callback = MagicMock()
        schedule_album_delay(30, 0, callback)
        mock_reactor.callLater.assert_called_once_with(30, callback)


class TestScheduleTrackDelay:
    @patch("indietracks_spider.utils.delay.time.sleep")
    @patch("indietracks_spider.utils.delay.random")
    def test_calls_sleep(self, mock_random, mock_sleep):
        mock_random.randint.return_value = 2
        from indietracks_spider.utils.delay import schedule_track_delay
        schedule_track_delay(1, 3)
        mock_sleep.assert_called_once_with(3)

    @patch("indietracks_spider.utils.delay.time.sleep")
    @patch("indietracks_spider.utils.delay.random")
    def test_zero_delay_no_sleep(self, mock_random, mock_sleep):
        mock_random.randint.return_value = 0
        from indietracks_spider.utils.delay import schedule_track_delay
        schedule_track_delay(0, 0)
        mock_sleep.assert_not_called()


class TestScheduleCircleDelay:
    @patch("indietracks_spider.utils.delay._get_reactor")
    def test_calls_reactor_calllater(self, mock_get_reactor):
        mock_reactor = MagicMock()
        mock_get_reactor.return_value = mock_reactor

        from indietracks_spider.utils.delay import schedule_circle_delay
        callback = MagicMock()
        schedule_circle_delay(5, callback)
        mock_reactor.callLater.assert_called_once_with(5, callback)
