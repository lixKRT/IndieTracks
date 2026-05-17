"""
JSON 配置读取工具。
"""

import json
from pathlib import Path
from typing import Any

# 爬虫项目根目录 = crawler/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


def load_json(filename: str) -> dict[str, Any]:
    """读取 config/ 目录下的 JSON 文件。"""
    path = CONFIG_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_delay_config() -> dict[str, Any]:
    """读取延迟策略配置，返回当前激活的那套。"""
    data = load_json("delay.json")
    active = data.get("active", "default")
    strategies = data.get("strategies", {})
    if active not in strategies:
        raise KeyError(f"延迟策略 '{active}' 不存在，可用: {list(strategies.keys())}")
    return strategies[active]


def get_database_config() -> dict[str, str]:
    """读取数据库连接配置。返回 dict 含 host/port/database/user/password。"""
    return load_json("database.json")
