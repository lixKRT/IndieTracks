"""IndieTracks 数据库建库建表脚本。"""
import sys
from pathlib import Path

from _common import (
    ROOT, CRAWLER_DIR, CONFIG_DIR,
    DB_CONFIG, SQL_FILE, INIT_FILE,
    find_psql, psql, read_json, write_json,
)


def main():
    print("=" * 60)
    print("  IndieTracks Database Setup")
    print("=" * 60)
    print()

    # ── [1/5] Find psql ──────────────────────────────
    print("[1/5] Find psql...")
    exe = find_psql()
    if not exe:
        print("  [ERROR] psql not found. Cannot continue.")
        input("Press Enter to exit...")
        sys.exit(1)
    print(f"  psql: {exe}")
    print()

    # ── [2/5] Check / fill database.json ─────────────
    print("[2/5] Check database.json...")
    cfg = read_json(DB_CONFIG)
    user = cfg.get("user", "")
    password = cfg.get("password", "")

    if not user or user == "请自行填写":
        user = input("  Enter PostgreSQL username (default: postgres): ").strip() or "postgres"
    if not password or password == "请自行填写":
        password = input(f"  Enter PostgreSQL password for {user}: ").strip()

    write_json(DB_CONFIG, {
        "host": "localhost",
        "port": 5432,
        "database": "indietracks",
        "user": user,
        "password": password,
    })
    print("  Config saved.")
    print()

    # ── [3/5] Test connection ────────────────────────
    print("[3/5] Test PostgreSQL connection...")
    result = psql("-U", user, "-d", "postgres", "-c", "SELECT 1", password=password)
    if result.returncode != 0:
        print("  [ERROR] Cannot connect to PostgreSQL.")
        print("  Make sure PostgreSQL service is running.")
        print(f"  stderr: {result.stderr}")
        input("Press Enter to exit...")
        sys.exit(1)
    print("  Connection OK")
    print()

    # ── [4/5] Create database + tables ───────────────
    print("[4/5] Create database and tables...")
    result = psql("-U", user, "-d", "postgres", "-f", str(SQL_FILE), password=password)
    if result.returncode != 0:
        print("  [ERROR] Failed to execute create_database.sql")
        print(result.stderr)
        input("Press Enter to exit...")
        sys.exit(1)
    print("  Done")
    print()

    # ── [5/5] Optional: reset data ───────────────────
    print("[5/5] Reset data (optional)...")
    choice = input("  Clear all data and reset sequences? [y/N]: ").strip().lower()
    if choice == "y":
        result = psql("-U", user, "-d", "indietracks", "-f", str(INIT_FILE), password=password)
        if result.returncode == 0:
            print("  Data cleared.")
        else:
            print("  [WARN] Failed:", result.stderr)
    else:
        print("  Skipped.")
    print()

    print("=" * 60)
    print("  Database setup complete!")
    print(f"  Database: indietracks")
    print(f"  User:     {user}")
    print("=" * 60)
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
