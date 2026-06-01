#!/bin/bash
# ============================================
# IndieTracks 爬虫一键部署脚本 (Linux)
# 新机器上运行此脚本即可完成：
#   1. 检查 Python 版本
#   2. 创建 venv + 安装依赖
#   3. 配置 database.json
#   4. 安装数据库（调用 setup-database.sh）
#   5. 安装 MinIO（调用 setup-minio.sh）
#   6. 运行单元测试验证
# ============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CRAWLER_DIR="$ROOT_DIR/crawler"
CONFIG_DIR="$CRAWLER_DIR/config"
DB_CONFIG="$CONFIG_DIR/database.json"
REQUIREMENTS="$CRAWLER_DIR/requirements.txt"
VENV_DIR="$CRAWLER_DIR/env"
VENV_PYTHON="$VENV_DIR/bin/python3"
VENV_PIP="$VENV_DIR/bin/pip"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
step() { echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${BLUE}  [$1/$TOTAL] $2${NC}"; echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"; }

TOTAL=6

echo "============================================"
echo "  IndieTracks Crawler — One-Click Setup"
echo "  爬虫项目一键部署"
echo "============================================"

# ── [1/6] Python 版本 ─────────────────────────────
step 1 "检查 Python 版本"

PYTHON_CMD=$(command -v python3 || command -v python || echo "")
if [ -z "$PYTHON_CMD" ]; then
    error "Python 未安装。请安装 Python 3.11+"
fi

PY_VER=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
info "Python $PY_VER"

PY_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]); then
    error "需要 Python 3.11+"
fi
info "版本检查通过"

# ── [2/6] 创建 venv + 安装依赖 ────────────────────
step 2 "创建 venv + 安装依赖"

if [ -f "$VENV_PYTHON" ]; then
    info "venv 已存在: $VENV_DIR"
    read -p "  是否重新创建 venv? [y/N]: " recreate
    if [ "$recreate" = "y" ] || [ "$recreate" = "Y" ]; then
        rm -rf "$VENV_DIR"
        info "旧 venv 已删除"
    fi
fi

if [ ! -f "$VENV_PYTHON" ]; then
    info "创建 venv..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    info "venv 创建完成"
fi

info "安装依赖..."
$VENV_PIP install -r "$REQUIREMENTS" -q
info "依赖安装完成"

# 验证 scrapy
SCAPY_VER=$($VENV_PYTHON -c "import scrapy; print(f'Scrapy {scrapy.__version__}')")
info "$SCAPY_VER"

# ── [3/6] 配置 database.json ──────────────────────
step 3 "配置 database.json"

if [ -f "$DB_CONFIG" ]; then
    DB_USER=$(python3 -c "import json; print(json.load(open('$DB_CONFIG')).get('user', ''))")
    DB_PASS=$(python3 -c "import json; print(json.load(open('$DB_CONFIG')).get('password', ''))")
fi

if [ -z "$DB_USER" ] || [ "$DB_USER" = "请自行填写" ]; then
    read -p "  PostgreSQL 用户名 (默认: postgres): " input_user
    DB_USER=${input_user:-postgres}
    read -p "  PostgreSQL 密码: " DB_PASS
else
    info "当前用户: $DB_USER"
    read -p "  保留此配置? [Y/n]: " keep
    if [ "$keep" = "n" ] || [ "$keep" = "N" ]; then
        read -p "  PostgreSQL 用户名 (默认: postgres): " input_user
        DB_USER=${input_user:-postgres}
        read -p "  PostgreSQL 密码: " DB_PASS
    fi
fi

if [ -z "$DB_PASS" ]; then
    read -p "  PostgreSQL 密码: " DB_PASS
fi

python3 -c "
import json
data = {
    'host': 'localhost',
    'port': 5432,
    'database': 'indietracks',
    'user': '$DB_USER',
    'password': '$DB_PASS'
}
with open('$DB_CONFIG', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
"
info "配置已保存: host=localhost port=5432 db=indietracks user=$DB_USER"

# ── [4/6] 安装数据库 ─────────────────────────────
step 4 "安装数据库"

if command -v psql &> /dev/null; then
    info "PostgreSQL 已安装: $(psql --version)"
else
    info "PostgreSQL 未安装，运行安装脚本..."
    bash "$SCRIPT_DIR/setup-database.sh"
fi

# 测试连接
export PGPASSWORD="$DB_PASS"
if psql -h localhost -U "$DB_USER" -d indietracks -c "SELECT 1" &> /dev/null; then
    info "数据库连接正常"
else
    warn "数据库连接失败，运行安装脚本..."
    bash "$SCRIPT_DIR/setup-database.sh"
fi

# ── [5/6] 安装 MinIO ─────────────────────────────
step 5 "安装 MinIO"

if curl -s "http://localhost:9000" > /dev/null 2>&1; then
    info "MinIO 正在运行: localhost:9000"
else
    info "MinIO 未运行，运行安装脚本..."
    bash "$SCRIPT_DIR/setup-minio.sh"
fi

# ── [6/6] 运行测试 ───────────────────────────────
step 6 "运行单元测试"

cd "$CRAWLER_DIR"
TEST_OUTPUT=$($VENV_PYTHON -m pytest tests/ -v --tb=short -q 2>&1)
TEST_EXIT=$?
echo "$TEST_OUTPUT" | tail -20

if [ $TEST_EXIT -ne 0 ]; then
    warn "部分测试失败"
else
    info "所有测试通过！"
fi

# ── 完成 ──────────────────────────────────────────
echo ""
echo "============================================"
echo "  部署完成！"
echo ""
echo "  快速开始:"
echo "    cd crawler"
echo "    source env/bin/activate"
echo "    scrapy crawl album_test"
echo ""
echo "  或使用启动器:"
echo "    bash scripts/linux/run-crawlers.sh"
echo "============================================"
echo ""
