"""共享常量。"""

import re

BASE = "https://www.dizzylab.net"
API_DISCS = f"{BASE}/apis/getdiscs/"
PAGE_SIZE = 24

# 曲目标题解析："1. 冬临之时 - Static World (02:48)"
TRACK_RE = re.compile(r"^\d+\.\s*(.+?)\s*\((\d{1,2}:\d{2})\)$")
