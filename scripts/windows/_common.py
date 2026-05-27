"""共享工具函数。"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CRAWLER_DIR = ROOT / "crawler"
CONFIG_DIR = CRAWLER_DIR / "config"
MINIO_EXE = ROOT / "tools" / "minio" / "minio.exe"
MC_EXE = ROOT / "tools" / "minio" / "mc.exe"
MINIO_DATA = ROOT / "database" / "minio-data"
DB_CONFIG = CONFIG_DIR / "database.json"
SPIDER_CONFIG = CONFIG_DIR / "spider.json"
MINIO_CONFIG = CONFIG_DIR / "minio.json"
SQL_FILE = ROOT / "database" / "create_database.sql"
INIT_FILE = ROOT / "database" / "init.sql"
VENV_ACTIVATE = CRAWLER_DIR / "env" / "Scripts" / "activate.bat"


_cached_psql: str | None = None


def find_psql() -> str | None:
    """查找 psql.exe，返回完整路径或 None。结果缓存，避免重复提示。"""
    global _cached_psql
    if _cached_psql is not None:
        return _cached_psql if _cached_psql else None

    # 1) 直接命令
    if shutil.which("psql"):
        _cached_psql = "psql"
        return "psql"

    # 2) 默认安装路径
    for ver in (18, 17, 16, 15):
        p = Path(f"C:/Program Files/PostgreSQL/{ver}/bin/psql.exe")
        if p.exists():
            _cached_psql = str(p)
            return str(p)

    # 3) 用户输入
    path = input("  psql.exe not found. Paste full path to psql.exe: ").strip().strip('"')
    if path and Path(path).exists():
        _cached_psql = path
        return path
    _cached_psql = ""
    return None


def psql(*args: str, password: str = "") -> subprocess.CompletedProcess:
    """执行 psql 命令。password 非空则通过 PGPASSWORD 环境变量传递。"""
    exe = find_psql()
    if not exe:
        raise RuntimeError("psql not found")
    env = None
    if password:
        import os
        env = os.environ.copy()
        env["PGPASSWORD"] = password
    return subprocess.run([exe, *args], capture_output=True, text=True, env=env)


def read_json(path: Path) -> dict:
    """安全读 JSON。"""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict):
    """安全写 JSON。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_scrapy(spider: str) -> int:
    """在 crawler/ 目录下运行 scrapy spider（使用 venv 中的 Python）。
    返回 exit code，Ctrl+C 时返回 2。
    """
    venv_python = CRAWLER_DIR / "env" / "Scripts" / "python.exe"
    if not venv_python.exists():
        print(f"  [ERROR] venv Python not found: {venv_python}")
        print("  Create it: cd crawler && python -m venv env && env\\Scripts\\pip install -r requirements.txt")
        return 1
    try:
        proc = subprocess.run(
            [str(venv_python), "-m", "scrapy", "crawl", spider],
            cwd=str(CRAWLER_DIR),
        )
        return proc.returncode
    except KeyboardInterrupt:
        print("\n  [INFO] Interrupted by user.")
        return 2


def check_minio() -> bool:
    """MinIO 是否在运行。"""
    import urllib.request
    try:
        urllib.request.urlopen("http://localhost:9000", timeout=2)
        return True
    except Exception:
        return False
