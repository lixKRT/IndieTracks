#!/bin/bash
# ============================================
# IndieTracks 本地存储检测脚本
# 报告 PostgreSQL + MinIO 存储占用，并可删除旧专辑文件释放空间。
# 由 run-crawlers.sh 在运行爬虫前调用。
# ============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CRAWLER_DIR="$ROOT_DIR/crawler"
CONFIG_DIR="$CRAWLER_DIR/config"
DB_CONFIG="$CONFIG_DIR/database.json"
MINIO_CONFIG="$CONFIG_DIR/minio.json"
VENV_PY="$CRAWLER_DIR/env/bin/python"
CHECK_PY="$SCRIPT_DIR/check_storage.py"

RED='\033[0;31m'
NC='\033[0m'

error() { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }

if [ ! -f "$VENV_PY" ]; then
    error "未找到爬虫 venv：$VENV_PY\n  请先运行: bash scripts/linux/setup-crawler.sh"
fi
if [ ! -f "$DB_CONFIG" ]; then
    error "未找到数据库配置：$DB_CONFIG"
fi
if [ ! -f "$MINIO_CONFIG" ]; then
    error "未找到 MinIO 配置：$MINIO_CONFIG"
fi
if [ ! -f "$CHECK_PY" ]; then
    error "未找到存储检测脚本：$CHECK_PY"
fi

export DB_CONFIG
export MINIO_CONFIG

exec "$VENV_PY" "$CHECK_PY"
