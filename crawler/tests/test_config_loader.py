"""config_loader.py 单元测试。"""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from indietracks_spider.utils.config_loader import (
    load_json,
    set_config_override,
    clear_config_overrides,
    get_delay_config,
    get_database_config,
    get_spider_config,
    get_minio_config,
)


class TestLoadJson:
    def test_load_from_override(self):
        set_config_override("test.json", {"key": "value"})
        result = load_json("test.json")
        assert result == {"key": "value"}

    def test_override_takes_precedence(self):
        set_config_override("database.json", {"host": "testhost"})
        result = load_json("database.json")
        assert result["host"] == "testhost"

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            load_json("nonexistent_file.json")


class TestConfigOverride:
    def test_set_and_clear(self):
        set_config_override("foo.json", {"a": 1})
        assert load_json("foo.json") == {"a": 1}
        clear_config_overrides()
        with pytest.raises(FileNotFoundError):
            load_json("foo.json")


class TestGetDelayConfig:
    def test_returns_active_strategy(self):
        set_config_override("delay.json", {
            "active": "default",
            "strategies": {
                "default": {"download_delay": 3, "between_albums_min": 60}
            }
        })
        result = get_delay_config()
        assert result["download_delay"] == 3
        assert result["between_albums_min"] == 60

    def test_missing_strategy_raises(self):
        set_config_override("delay.json", {
            "active": "nonexistent",
            "strategies": {"default": {}}
        })
        with pytest.raises(KeyError):
            get_delay_config()


class TestGetDatabaseConfig:
    def test_returns_config(self):
        set_config_override("database.json", {
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "user": "testuser",
            "password": "testpass",
        })
        result = get_database_config()
        assert result["host"] == "localhost"
        assert result["port"] == 5432


class TestGetSpiderConfig:
    def test_returns_config(self):
        set_config_override("spider.json", {"mode": "full", "max_albums": 50})
        result = get_spider_config()
        assert result["mode"] == "full"
        assert result["max_albums"] == 50


class TestGetMinioConfig:
    def test_returns_config(self):
        set_config_override("minio.json", {"endpoint": "localhost:9000", "bucket": "test"})
        result = get_minio_config()
        assert result["endpoint"] == "localhost:9000"
