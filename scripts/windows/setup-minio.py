"""IndieTracks MinIO 一键部署脚本。"""
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from _common import (
    ROOT, MINIO_EXE, MC_EXE, MINIO_DATA, MINIO_CONFIG,
    write_json, check_minio,
)

ROOT_USER = "admin"
ROOT_PASS = "indietracks2026"
APP_USER = "indietracks_app"
APP_PASS = "indietracks_app_2026"


def download(url: str, dest: Path) -> bool:
    """下载文件，返回是否成功。"""
    print(f"  Downloading {dest.name}...")
    import urllib.request
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, str(dest))
        return True
    except Exception as e:
        print(f"  [ERROR] Download failed: {e}")
        return False


def mc(*args: str) -> subprocess.CompletedProcess:
    """执行 mc 命令。"""
    return subprocess.run(
        [str(MC_EXE), *args],
        capture_output=True, text=True,
    )


def main():
    print("=" * 60)
    print("  IndieTracks MinIO Setup")
    print("=" * 60)
    print()

    # ── [1/5] Check MinIO server ─────────────────────
    print("[1/5] Check MinIO server...")
    if MINIO_EXE.exists():
        print("  minio.exe found, skip download")
    else:
        if not download(
            "https://dl.min.io/server/minio/release/windows-amd64/minio.exe",
            MINIO_EXE,
        ):
            input("Press Enter to exit...")
            sys.exit(1)
        print("  Done")
    print()

    # ── [2/5] Check MinIO client (mc) ────────────────
    print("[2/5] Check MinIO client (mc)...")
    if MC_EXE.exists():
        print("  mc.exe found, skip download")
    else:
        if not download(
            "https://dl.min.io/client/mc/release/windows-amd64/mc.exe",
            MC_EXE,
        ):
            input("Press Enter to exit...")
            sys.exit(1)
        print("  Done")
    print()

    # ── [3/5] Start MinIO ────────────────────────────
    print("[3/5] Start MinIO...")
    MINIO_DATA.mkdir(parents=True, exist_ok=True)
    print(f"  Data dir: {MINIO_DATA}")

    if check_minio():
        print("  MinIO already running")
    else:
        print("  Starting MinIO server...")
        subprocess.Popen(
            [str(MINIO_EXE), "server", str(MINIO_DATA), "--console-address", ":9001"],
            env={**__import__("os").environ, "MINIO_ROOT_USER": ROOT_USER, "MINIO_ROOT_PASSWORD": ROOT_PASS},
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        print("  Waiting for MinIO to start (max 30s)...")
        for i in range(30):
            time.sleep(1)
            if check_minio():
                print(f"  MinIO started after {i + 1}s")
                break
        else:
            print("  [WARN] MinIO did not start within 30s, proceeding anyway...")
    print()

    # ── [4/5] Configure bucket + access key ──────────
    print("[4/5] Configure bucket and access key...")

    # alias
    mc("alias", "set", "local", "http://localhost:9000", ROOT_USER, ROOT_PASS)

    # bucket
    r = mc("mb", "local/indietracks")
    if r.returncode != 0:
        print("  bucket may already exist")

    # user
    r = mc("admin", "user", "add", "local", APP_USER, APP_PASS)
    if r.returncode != 0:
        print("  user may already exist")

    # policy
    r = mc("admin", "policy", "attach", "local", "readwrite", "--user", APP_USER)
    if r.returncode != 0:
        print("  policy may already be attached")

    print("  Done")
    print()

    # ── [5/5] Write config ───────────────────────────
    print("[5/5] Write config file...")
    write_json(MINIO_CONFIG, {
        "endpoint": "http://localhost:9000",
        "access_key": APP_USER,
        "secret_key": APP_PASS,
        "bucket": "indietracks",
        "prefixes": {
            "audio_preview": "audio/preview/",
            "audio_full": "audio/full/",
            "covers": "covers/",
            "logos": "logos/",
            "avatars": "avatars/",
        },
    })
    print(f"  Config written: {MINIO_CONFIG}")
    print()

    print("=" * 60)
    print("  Setup complete!")
    print(f"  MinIO API:       http://localhost:9000")
    print(f"  MinIO Console:   http://localhost:9001")
    print(f"  Root:            {ROOT_USER} / {ROOT_PASS}")
    print(f"  App:             {APP_USER} / {APP_PASS}")
    print("=" * 60)
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
