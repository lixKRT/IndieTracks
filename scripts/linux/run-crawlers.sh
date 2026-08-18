#!/bin/bash
# ============================================
# IndieTracks 爬虫启动器 (Linux)
# 前置检查 → 选择模式 → 运行爬虫
# ============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CRAWLER_DIR="$ROOT_DIR/crawler"
CONFIG_DIR="$CRAWLER_DIR/config"
DB_CONFIG="$CONFIG_DIR/database.json"
SPIDER_CONFIG="$CONFIG_DIR/spider.json"
VENV_ACTIVATE="$CRAWLER_DIR/env/bin/activate"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
step() { echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${BLUE}  $1${NC}"; echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"; }

banner() {
    echo "============================================"
    echo "  $1"
    echo "============================================"
    echo ""
}

# 读取 JSON 配置
read_json() {
    if [ -f "$1" ]; then
        python3 -c "import json; print(json.dumps(json.load(open('$1')), ensure_ascii=False))"
    else
        echo "{}"
    fi
}

# 获取 JSON 字段
get_json_field() {
    python3 -c "import json; d=json.load(open('$1')); print(d.get('$2', ''))"
}

# 写入 JSON 配置
write_json() {
    python3 -c "
import json
data = $2
with open('$1', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
"
}

# 运行爬虫
run_scrapy() {
    local spider=$1
    info "运行爬虫: $spider"
    cd "$CRAWLER_DIR"
    source "$VENV_ACTIVATE"
    scrapy crawl "$spider"
    local exit_code=$?
    if [ $exit_code -eq 2 ]; then
        warn "用户中断 (Ctrl+C)"
    elif [ $exit_code -ne 0 ]; then
        error "爬虫 $spider 失败 (exit code: $exit_code)"
    fi
}

banner "IndieTracks Crawler Launcher"

# ── Pre 1: venv ─────────────────────────────────
step "[Pre 1/5] 检查 Python venv"
if [ ! -f "$VENV_ACTIVATE" ]; then
    error "venv 不存在: $VENV_ACTIVATE\n  创建: cd crawler && python3 -m venv env && source env/bin/activate && pip install -r requirements.txt"
fi
info "venv OK"

# ── Pre 2: psql ─────────────────────────────────
step "[Pre 2/5] 检查 psql"
if ! command -v psql &> /dev/null; then
    error "psql 未安装。请安装 PostgreSQL 客户端: apt install postgresql-client"
fi
info "psql: $(which psql)"

# ── Pre 3: database credentials ─────────────────
step "[Pre 3/5] 检查数据库配置"
DB_USER=$(get_json_field "$DB_CONFIG" "user")
DB_PASS=$(get_json_field "$DB_CONFIG" "password")

if [ -z "$DB_USER" ] || [ "$DB_USER" = "请自行填写" ]; then
    read -p "  PostgreSQL 用户名 (默认: postgres): " input_user
    DB_USER=${input_user:-postgres}
    read -p "  PostgreSQL 密码: " DB_PASS
    write_json "$DB_CONFIG" "{
        'host': 'localhost',
        'port': 5432,
        'database': 'indietracks',
        'user': '$DB_USER',
        'password': '$DB_PASS'
    }"
    info "配置已保存"
else
    info "数据库配置 OK ($DB_USER@localhost)"
fi

# ── Pre 4: database + tables ────────────────────
step "[Pre 4/5] 检查数据库和表"
export PGPASSWORD="$DB_PASS"
if psql -h localhost -U "$DB_USER" -d indietracks -c "SELECT COUNT(*) FROM albums" &> /dev/null; then
    info "数据库 + 表 OK"
else
    warn "数据库或表不存在，运行数据库初始化..."
    bash "$SCRIPT_DIR/setup-database.sh"
    if ! psql -h localhost -U "$DB_USER" -d indietracks -c "SELECT COUNT(*) FROM albums" &> /dev/null; then
        error "数据库初始化失败"
    fi
fi

# ── Pre 5: MinIO ────────────────────────────────
step "[Pre 5/5] 检查 MinIO"
if curl -s "http://localhost:9000" > /dev/null 2>&1; then
    info "MinIO OK"
else
    warn "MinIO 未运行，运行 MinIO 初始化..."
    bash "$SCRIPT_DIR/setup-minio.sh"
fi

# ── Storage check ─────────────────────────────
step "本地存储检测"
if [ -f "$SCRIPT_DIR/check-storage.sh" ]; then
    bash "$SCRIPT_DIR/check-storage.sh"
else
    error "本地存储检测脚本不存在: $SCRIPT_DIR/check-storage.sh"
fi

# ── Mode ────────────────────────────────────────
banner "选择爬取模式"
echo "  [1] 首次爬取 (full 模式，依次运行所有爬虫)"
echo "  [2] 增量更新 (选择爬虫)"
echo ""
read -p "  请选择 [1/2]: " mode_choice

if [ "$mode_choice" = "1" ]; then
    # ── 首次爬取 ────────────────────────────────
    step "首次爬取"
    read -p "  最大爬取专辑数 (默认 20): " max_albums
    max_albums=${max_albums:-20}
    read -p "  最大爬取用户数 (默认 10): " max_users
    max_users=${max_users:-10}

    write_json "$SPIDER_CONFIG" "{
        'mode': 'full',
        'max_albums': $max_albums,
        'max_users': $max_users
    }"

    echo ""
    info "模式: full"
    info "专辑: $max_albums"
    info "用户: $max_users"
    echo ""

    SEQUENCE=("album_bulk" "album_incremental" "circle" "user_roles" "user_pages")
    for i in "${!SEQUENCE[@]}"; do
        step "[$(($i+1))/${#SEQUENCE[@]}] ${SEQUENCE[$i]}"
        run_scrapy "${SEQUENCE[$i]}"
    done

    # 最终全量刷新
    step "[$((${#SEQUENCE[@]}+1))/${#SEQUENCE[@]}] album_bulk (全量刷新)"
    echo "  这将爬取所有剩余专辑。"
    read -p "  是否运行全量刷新? [y/N]: " do_full
    if [ "$do_full" = "y" ] || [ "$do_full" = "Y" ]; then
        write_json "$SPIDER_CONFIG" "{
            'mode': 'full',
            'max_albums': 0,
            'max_users': 0
        }"
        run_scrapy "album_bulk"
    fi

elif [ "$mode_choice" = "2" ]; then
    # ── 增量更新 ────────────────────────────────
    step "增量更新"
    read -p "  每个爬虫最大专辑数 (默认 0=不限): " max_albums
    max_albums=${max_albums:-0}
    read -p "  每个爬虫最大用户数 (默认 10): " max_users
    max_users=${max_users:-10}

    write_json "$SPIDER_CONFIG" "{
        'mode': 'incremental',
        'max_albums': $max_albums,
        'max_users': $max_users
    }"

    echo ""
    echo "  选择要运行的爬虫 (输入编号，逗号分隔，如 1,3,5):"
    echo ""
    echo "    [1] album_bulk (incremental)"
    echo "    [2] album_incremental (追新)"
    echo "    [3] circle (社团描述+logo+成员ID)"
    echo "    [4] user_roles (STAFF/PRO)"
    echo "    [5] user_pages (已购/收藏/关注)"
    echo "    [6] album_bulk (full refresh, max=0)"
    echo "    [0] 全部运行"
    echo ""
    read -p "  请选择: " sel

    if [ "$sel" = "0" ]; then
        sel="1,2,3,4,5,6"
    fi

    IFS=',' read -ra SELECTED <<< "$sel"
    for num in "${SELECTED[@]}"; do
        num=$(echo "$num" | tr -d ' ')
        case $num in
            1) step "album_bulk (incremental)"; run_scrapy "album_bulk" ;;
            2) step "album_incremental"; run_scrapy "album_incremental" ;;
            3) step "circle"; run_scrapy "circle" ;;
            4) step "user_roles"; run_scrapy "user_roles" ;;
            5) step "user_pages"; run_scrapy "user_pages" ;;
            6)
                step "album_bulk (full refresh)"
                write_json "$SPIDER_CONFIG" "{
                    'mode': 'full',
                    'max_albums': 0,
                    'max_users': 0
                }"
                run_scrapy "album_bulk"
                ;;
        esac
    done
else
    error "无效选择"
fi

# ── 完成 ────────────────────────────────────────
echo ""
echo "============================================"
echo "  爬取完成！"
echo "============================================"
echo ""
