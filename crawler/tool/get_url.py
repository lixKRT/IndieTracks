"""
Dizzylab 网页源码获取工具。

用法：
    python get_url.py "https://www.dizzylab.net/d/SW20/" [输出文件名]

不加输出文件名则自动按页面标题命名，保存到 url/ 目录。
"""

import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests

# ── 请求头（伪装浏览器） ──────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/url,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def slugify_url(url: str) -> str:
    """从 URL 路径提取一个安全的文件名片段。"""
    path = urlparse(url).path.strip("/")
    if not path:
        return "index"
    parts = [unquote(p) for p in path.split("/")]
    name = "_".join(parts[-2:]) if len(parts) >= 2 else parts[-1]
    name = re.sub(r"[^\w\-\.]", "_", name)
    return name or "page"


def get_html(
    url: str,
    out_dir: str = "url",
    out_file: str | None = None,
    timeout: int = 30,
) -> Path:
    """
    获取网页源码并保存到文件。

    Args:
        url: 目标 URL
        out_dir: 输出目录（相对于脚本所在目录）
        out_file: 输出文件名（不含路径）。为 None 时自动生成
        timeout: 请求超时秒数

    Returns:
        保存的文件 Path
    """
    print(f"[GET] {url}")
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = "utf-8"

    html = resp.text
    print(f"      状态 {resp.status_code} | {len(html)} 字符 | {resp.headers.get('content-type', '?')}")

    base = Path(__file__).resolve().parent
    out_path = base / out_dir
    out_path.mkdir(parents=True, exist_ok=True)

    if out_file is None:
        out_file = f"{slugify_url(url)}.url"

    file_path = out_path / out_file
    file_path.write_text(html, encoding="utf-8")
    print(f"      已保存 → {file_path.resolve()}")
    return file_path


def main():
    if len(sys.argv) < 2:
        print("用法: python get_url.py <URL> [输出文件名]")
        print("示例: python get_url.py \"https://www.dizzylab.net/d/SW20/\"")
        sys.exit(1)

    url = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else None
    get_html(url, out_file=out_file)


if __name__ == "__main__":
    main()
