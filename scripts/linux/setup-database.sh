#!/bin/bash
# ============================================
# IndieTracks 数据库部署脚本
# 安装 PostgreSQL 18 + 建库建表
# ============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
SQL_FILE="$ROOT_DIR/database/create_database.sql"
ENV_FILE="$SCRIPT_DIR/.env"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo "============================================"
echo "  IndieTracks Database Setup"
echo "============================================"
echo ""

# ── [1/5] 加载环境变量 ─────────────────────
info "[1/5] 加载环境变量..."
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

DB_USER="${DB_USER:-postgres}"
DB_PASS="${DB_PASS:-postgres}"
DB_NAME="${DB_NAME:-indietracks}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

info "  数据库: $DB_NAME"
info "  用户: $DB_USER"
info "  地址: $DB_HOST:$DB_PORT"
echo ""

# ── [2/5] 检查 PostgreSQL ──────────────────
info "[2/5] 检查 PostgreSQL..."
if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version | grep -oP '\d+' | head -1)
    info "  PostgreSQL 已安装: $(psql --version)"
else
    info "  PostgreSQL 未安装，开始安装..."

    # 添加 PostgreSQL 官方 APT 源
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update

    # 安装 PostgreSQL 18
    sudo apt-get install -y postgresql-18 postgresql-client-18

    # 启动服务
    sudo systemctl start postgresql
    sudo systemctl enable postgresql

    info "  PostgreSQL 18 安装完成"
fi
echo ""

# ── [3/5] 测试连接 ─────────────────────────
info "[3/5] 测试 PostgreSQL 连接..."
export PGPASSWORD="$DB_PASS"

if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT 1" &> /dev/null; then
    info "  连接成功"
else
    warn "  连接失败，尝试创建用户..."
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" 2>/dev/null || true
    sudo -u postgres psql -c "ALTER USER $DB_USER WITH SUPERUSER;" 2>/dev/null || true
    info "  用户创建/更新完成"
fi
echo ""

# ── [4/5] 建库建表 ─────────────────────────
info "[4/5] 创建数据库和表..."

# 检查数据库是否存在
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
    info "  数据库 $DB_NAME 已存在"
else
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"
    info "  数据库 $DB_NAME 创建完成"
fi

# 检查表是否存在（检查 albums 表作为代表）
TABLE_EXISTS=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name='albums')" 2>/dev/null)

if [ "$TABLE_EXISTS" = "t" ]; then
    info "  表已存在，跳过建表"
else
    if [ -f "$SQL_FILE" ]; then
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$SQL_FILE"
        info "  建表完成"
    else
        error "  SQL 文件不存在: $SQL_FILE"
    fi
fi
echo ""

# ── [5/5] 完成 ─────────────────────────────
echo "============================================"
echo "  数据库部署完成！"
echo "  数据库: $DB_NAME"
echo "  用户: $DB_USER"
echo "  地址: $DB_HOST:$DB_PORT"
echo "============================================"
echo ""
