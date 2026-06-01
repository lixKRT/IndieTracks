#!/bin/bash
# ============================================
# IndieTracks 部署脚本
# 构建前端和后端，重启服务
# ============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
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
echo "  IndieTracks 部署"
echo "============================================"
echo ""

# ── 检查环境变量 ───────────────────────────
if [ ! -f "$ENV_FILE" ]; then
    error ".env 文件不存在。请先运行 setup-all.sh"
fi
source "$ENV_FILE"

# ── 构建前端 ───────────────────────────────
info "构建前端..."
cd "$ROOT_DIR/frontend"
npm install
npm run build
info "前端构建完成"

# ── 构建后端 ───────────────────────────────
info "构建后端..."
cd "$ROOT_DIR/backend"
export JAVA_HOME=/usr/lib/jvm/java-25-amazon-corretto

# 复制生产环境配置
cp "$SCRIPT_DIR/application-prod.properties" "$ROOT_DIR/backend/"

if [ -f "./mvnw" ]; then
    ./mvnw clean package -DskipTests
else
    mvn clean package -DskipTests
fi
info "后端构建完成"

# ── 重启服务 ───────────────────────────────
info "重启 Nginx..."
nginx -t && systemctl reload nginx

info "重启后端服务..."
systemctl restart indietracks

# ── 完成 ───────────────────────────────────
echo ""
echo "============================================"
echo "  部署完成！"
echo "============================================"
echo ""
echo "  查看后端状态: sudo systemctl status indietracks"
echo "  查看实时日志: sudo journalctl -u indietracks -f"
echo ""
