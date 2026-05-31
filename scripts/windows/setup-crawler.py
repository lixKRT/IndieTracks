"""IndieTracks 爬虫一键部署脚本。

新机器上运行此脚本即可完成：
  1. 检查 Python 版本
  2. 创建 venv + 安装依赖
  3. 配置 database.json（交互填写）
  4. 测试数据库连接 + 建表
  5. 检查 MinIO（可选）
  6. 运行单元测试验证
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent.parent
CRAWLER_DIR = ROOT / "crawler"
CONFIG_DIR = CRAWLER_DIR / "config"
DB_CONFIG = CONFIG_DIR / "database.json"
MINIO_CONFIG = CONFIG_DIR / "minio.json"
REQUIREMENTS = CRAWLER_DIR / "requirements.txt"
VENV_DIR = CRAWLER_DIR / "env"
VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
VENV_PIP = VENV_DIR / "Scripts" / "pip.exe"
SQL_FILE = ROOT / "database" / "create_database.sql"


def step(n: int, total: int, msg: str):
    print(f"\n[{n}/{total}] {msg}")
    print("-" * 50)


def ask(prompt: str, default: str = "") -> str:
    suffix = f" (default: {default})" if default else ""
    val = input(f"  {prompt}{suffix}: ").strip()
    return val if val else default


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    import json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict):
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_psql() -> str | None:
    import shutil
    if shutil.which("psql"):
        return "psql"
    for ver in (18, 17, 16, 15):
        p = Path(f"C:/Program Files/PostgreSQL/{ver}/bin/psql.exe")
        if p.exists():
            return str(p)
    return None


def psql_exec(*args: str, password: str = "") -> subprocess.CompletedProcess:
    exe = find_psql()
    if not exe:
        raise RuntimeError("psql not found")
    env = None
    if password:
        import os
        env = os.environ.copy()
        env["PGPASSWORD"] = password
    return subprocess.run([exe, *args], capture_output=True, text=True, env=env)


def check_minio() -> bool:
    import urllib.request
    try:
        urllib.request.urlopen("http://localhost:9000", timeout=2)
        return True
    except Exception:
        return False


def main():
    TOTAL = 6

    print("=" * 60)
    print("  IndieTracks Crawler — One-Click Setup")
    print("  爬虫项目一键部署")
    print("=" * 60)

    # ── [1/6] Python 版本 ─────────────────────────────
    step(1, TOTAL, "Check Python version")
    ver = sys.version_info
    print(f"  Python {ver.major}.{ver.minor}.{ver.micro}")
    if ver < (3, 11):
        print("  [ERROR] Python 3.11+ required!")
        input("\nPress Enter to exit...")
        sys.exit(1)
    print("  OK")

    # ── [2/6] 创建 venv + 安装依赖 ────────────────────
    step(2, TOTAL, "Create venv + install dependencies")

    if VENV_PYTHON.exists():
        print(f"  venv already exists: {VENV_DIR}")
        choice = ask("Recreate venv? [y/N]", "n")
        if choice == "y":
            import shutil
            shutil.rmtree(VENV_DIR)
            print("  Old venv removed.")

    if not VENV_PYTHON.exists():
        print("  Creating venv...")
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"  [ERROR] Failed to create venv: {result.stderr}")
            input("\nPress Enter to exit...")
            sys.exit(1)
        print("  venv created.")

    print("  Installing dependencies...")
    result = subprocess.run(
        [str(VENV_PIP), "install", "-r", str(REQUIREMENTS), "-q"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  [ERROR] pip install failed: {result.stderr}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    print("  Dependencies installed.")

    # 验证 scrapy 可用
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", "import scrapy; print(f'Scrapy {scrapy.__version__}')"],
        capture_output=True, text=True,
    )
    print(f"  {result.stdout.strip()}")

    # ── [3/6] 配置 database.json ──────────────────────
    step(3, TOTAL, "Configure database.json")

    cfg = read_json(DB_CONFIG)
    user = cfg.get("user", "")
    password = cfg.get("password", "")

    if not user or user == "请自行填写":
        user = ask("PostgreSQL username", "postgres")
    else:
        print(f"  Current user: {user}")
        choice = ask("Keep this config? [Y/n]", "y")
        if choice == "n":
            user = ask("PostgreSQL username", "postgres")
            password = ""

    if not password or password == "请自行填写":
        password = ask(f"PostgreSQL password for {user}")

    write_json(DB_CONFIG, {
        "host": "localhost",
        "port": 5432,
        "database": "indietracks",
        "user": user,
        "password": password,
    })
    print(f"  Saved: host=localhost port=5432 db=indietracks user={user}")

    # ── [4/6] 测试数据库 + 建表 ──────────────────────
    step(4, TOTAL, "Test database connection + create tables")

    psql_path = find_psql()
    if not psql_path:
        print("  [WARN] psql not found. Skipping DB setup.")
        print("  Install PostgreSQL and run: python scripts/windows/setup-database.py")
    else:
        print(f"  psql: {psql_path}")

        # 测试连接
        result = psql_exec("-U", user, "-d", "postgres", "-c", "SELECT 1", password=password)
        if result.returncode != 0:
            print(f"  [ERROR] Cannot connect: {result.stderr.strip()}")
            print("  Make sure PostgreSQL is running.")
            input("\nPress Enter to exit...")
            sys.exit(1)
        print("  Connection OK")

        # 建库建表
        print("  Creating database + tables...")
        result = psql_exec("-U", user, "-d", "postgres", "-f", str(SQL_FILE), password=password)
        if result.returncode != 0:
            print(f"  [WARN] SQL execution issue: {result.stderr.strip()}")
        else:
            print("  Database 'indietracks' ready, tables created.")

    # ── [5/6] 检查 MinIO ─────────────────────────────
    step(5, TOTAL, "Check MinIO (optional)")

    if check_minio():
        print("  MinIO is running on localhost:9000")
    else:
        print("  MinIO not detected.")
        print("  Audio/image upload will fail without MinIO.")
        print("  To set up: python scripts/windows/setup-minio.py")

    # ── [6/6] 运行测试 ───────────────────────────────
    step(6, TOTAL, "Run unit tests")

    result = subprocess.run(
        [str(VENV_PYTHON), "-m", "pytest", "tests/", "-v", "--tb=short", "-q"],
        cwd=str(CRAWLER_DIR),
        capture_output=True, text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"  [WARN] Some tests failed:")
        print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
    else:
        print("  All tests passed!")

    # ── 完成 ──────────────────────────────────────────
    print()
    print("=" * 60)
    print("  Setup complete!")
    print()
    print("  Quick start:")
    print(f"    cd crawler")
    print(f"    .\\env\\Scripts\\activate")
    print(f"    scrapy crawl album_test")
    print()
    print("  Or use the launcher:")
    print(f"    python scripts/windows/run-crawlers.py")
    print("=" * 60)
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
