"""IndieTricks Crawler Launcher."""
import subprocess
import sys
from pathlib import Path

from _common import (
    ROOT, CRAWLER_DIR, CONFIG_DIR,
    DB_CONFIG, SPIDER_CONFIG,
    find_psql, psql, read_json, write_json, run_scrapy, check_minio,
)


SEQUENCE = [
    ("album_bulk",     "album_bulk (full)"),
    ("album_incremental", "album_incremental"),
    ("circle_members", "circle_members"),
    ("user_roles",     "user_roles"),
    ("user_pages",     "user_pages"),
]

INCREMENTAL_OPTIONS = [
    ("1", "album_bulk",       "album_bulk (incremental)"),
    ("2", "album_incremental", "album_incremental"),
    ("3", "circle_members",   "circle_members"),
    ("4", "user_roles",       "user_roles"),
    ("5", "user_pages",       "user_pages"),
    ("6", "album_bulk_full",  "album_bulk (full refresh, max=0)"),
]


def banner(title: str):
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()


def ensure_venv():
    venv_py = CRAWLER_DIR / "env" / "Scripts" / "python.exe"
    if not venv_py.exists():
        print(f"  [ERROR] venv not found: {venv_py}")
        print("  Create it: cd crawler && python -m venv env")
        return False
    return True


def ensure_db_credentials():
    cfg = read_json(DB_CONFIG)
    user = cfg.get("user", "")
    password = cfg.get("password", "")

    if not user or user == "请自行填写":
        user = input("  Enter PostgreSQL username (default: postgres): ").strip() or "postgres"
        password = input(f"  Enter PostgreSQL password: ").strip()
        write_json(DB_CONFIG, {
            "host": "localhost",
            "port": 5432,
            "database": "indietracks",
            "user": user,
            "password": password,
        })
        print("  Config saved.")
    else:
        print(f"  Credentials OK ({user}@localhost)")
    return user, password


def ensure_db_tables(user: str, password: str):
    result = psql("-U", user, "-d", "indietracks", "-c", "SELECT COUNT(*) FROM albums", password=password)
    return result.returncode == 0


def main():
    banner("IndieTracks Crawler Launcher")

    # ── Pre 1: venv ─────────────────────────────────
    print("[Pre 1/5] Check Python venv...")
    if not ensure_venv():
        input("Press Enter to exit...")
        sys.exit(1)
    print("  venv OK")
    print()

    # ── Pre 2: psql ─────────────────────────────────
    print("[Pre 2/5] Find psql...")
    exe = find_psql()
    if not exe:
        print("  [ERROR] psql not found.")
        input("Press Enter to exit...")
        sys.exit(1)
    print(f"  psql: {exe}")
    print()

    # ── Pre 3: database credentials ─────────────────
    print("[Pre 3/5] Check database credentials...")
    user, password = ensure_db_credentials()
    print()

    # ── Pre 4: database + tables ────────────────────
    print("[Pre 4/5] Check database and tables...")
    if not ensure_db_tables(user, password):
        print("  Database or tables not found.")
        print("  Launching database setup...")
        subprocess.run([sys.executable, str(Path(__file__).parent / "setup-database.py")])
        if not ensure_db_tables(user, password):
            print("  [ERROR] Database setup failed.")
            input("Press Enter to exit...")
            sys.exit(1)
    else:
        print("  Database + tables OK")
    print()

    # ── Pre 5: MinIO ────────────────────────────────
    print("[Pre 5/5] Check MinIO...")
    if check_minio():
        print("  MinIO OK")
    else:
        print("  MinIO is not running.")
        print("  Launching MinIO setup...")
        subprocess.run([sys.executable, str(Path(__file__).parent / "setup-minio.py")])
    print()

    # ── Mode ────────────────────────────────────────
    banner("Select crawl mode")
    print("  [1] First crawl (full mode, sequential all spiders)")
    print("  [2] Incremental update (choose spiders)")
    print()
    choice = input("  Enter choice [1/2]: ").strip()

    if choice == "1":
        first_crawl()
    elif choice == "2":
        incremental()
    else:
        print("  Invalid choice.")
        input("Press Enter to exit...")
        sys.exit(1)


def first_crawl():
    albums = input("  Max albums to crawl (default 20): ").strip()
    max_albums = int(albums) if albums else 20
    users = input("  Max users to crawl (default 10): ").strip()
    max_users = int(users) if users else 10

    write_json(SPIDER_CONFIG, {
        "mode": "full",
        "max_albums": max_albums,
        "max_users": max_users,
    })

    print()
    print(f"  Mode:   full")
    print(f"  Albums: {max_albums}")
    print(f"  Users:  {max_users}")
    print()

    for i, (spider, label) in enumerate(SEQUENCE, 1):
        print(f"  ----[{i}/{len(SEQUENCE)}] {label}----")
        run_scrapy(spider)
        print()

    # Final full refresh
    print(f"  ----[6/6] album_bulk (full refresh, max=0)----")
    print("  This will crawl ALL remaining albums.")
    do_full = input("  Run final full refresh? [y/N]: ").strip().lower()
    if do_full == "y":
        write_json(SPIDER_CONFIG, {
            "mode": "full",
            "max_albums": 0,
            "max_users": 0,
        })
        run_scrapy("album_bulk")

    done()


def incremental():
    albums = input("  Max albums per spider (default 0=unlimited): ").strip()
    max_albums = int(albums) if albums else 0
    users = input("  Max users per spider (default 10): ").strip()
    max_users = int(users) if users else 10

    write_json(SPIDER_CONFIG, {
        "mode": "incremental",
        "max_albums": max_albums,
        "max_users": max_users,
    })

    print()
    print("  Select spiders to run (enter numbers, e.g. 1,3,5):")
    print()
    for num, _, label in INCREMENTAL_OPTIONS:
        print(f"    [{num}] {label}")
    print("    [0] All of the above")
    print()
    sel = input("  Your choice: ").strip()

    if sel == "0":
        selected = [opt for opt in INCREMENTAL_OPTIONS if opt[0] != "0"]
    else:
        nums = {s.strip() for s in sel.split(",")}
        selected = [opt for opt in INCREMENTAL_OPTIONS if opt[0] in nums]

    print()
    for num, spider, label in selected:
        print(f"  ---- {label} ----")
        if spider == "album_bulk_full":
            write_json(SPIDER_CONFIG, {
                "mode": "full",
                "max_albums": 0,
                "max_users": 0,
            })
            run_scrapy("album_bulk")
        else:
            run_scrapy(spider)
        print()

    done()


def done():
    print("=" * 60)
    print("  Crawl session complete!")
    print("=" * 60)
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
