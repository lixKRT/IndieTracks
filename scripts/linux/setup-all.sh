#!/bin/bash
# ============================================
# IndieTracks 一键部署脚本
# 依次调用所有子脚本完成部署
# ============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
ENV_EXAMPLE="$SCRIPT_DIR/.env.example"

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

echo "============================================"
echo "  IndieTracks 一键部署"
echo "============================================"
echo ""

# ── [1/8] 检查环境变量文件 ─────────────────
step "[1/8] 检查环境变量文件"

if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$ENV_EXAMPLE" ]; then
        warn ".env 文件不存在，正在从模板创建..."
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        warn "请编辑 $ENV_FILE 填写实际配置，然后重新运行此脚本"
        exit 1
    else
        error ".env.example 文件不存在"
    fi
fi

info ".env 文件已就绪"
source "$ENV_FILE"

# ── [2/8] 安装 JDK 25 ─────────────────────
step "[2/8] 安装 JDK 25 (Amazon Corretto)"

if command -v java &> /dev/null; then
    JAVA_VER=$(java -version 2>&1 | head -1)
    info "Java 已安装: $JAVA_VER"
else
    info "安装 Amazon Corretto JDK 25..."
    apt-get install -y curl gnupg
    curl -fsSL https://apt.corretto.aws/corretto.key | gpg --dearmor -o /usr/share/keyrings/corretto.gpg
    echo "deb [signed-by=/usr/share/keyrings/corretto.gpg] https://apt.corretto.aws stable main" > /etc/apt/sources.list.d/corretto.list
    apt-get update
    apt-get install -y java-25-amazon-corretto-jdk
    info "JDK 25 安装完成"
fi

# ── [3/8] 检查 Node.js ─────────────────────
step "[3/8] 检查 Node.js"

if command -v node &> /dev/null; then
    NODE_VER=$(node --version)
    info "Node.js: $NODE_VER"
else
    error "Node.js 未安装。请安装 Node.js 20+"
fi

# ── [4/8] 安装数据库 ───────────────────────
step "[4/8] 安装数据库"
bash "$SCRIPT_DIR/setup-database.sh"

# ── [5/8] 安装 MinIO ──────────────────────
step "[5/8] 安装 MinIO"
mkdir -p "$ROOT_DIR/logs"
bash "$SCRIPT_DIR/setup-minio.sh"

# ── [6/8] 构建前端 ─────────────────────────
step "[6/8] 构建前端"

cd "$ROOT_DIR/frontend"
info "安装依赖..."
npm install
info "构建前端..."
npm run build
info "前端构建完成"

# ── [7/8] 构建后端 ─────────────────────────
step "[7/8] 构建后端"

cd "$ROOT_DIR/backend"
export JAVA_HOME=/usr/lib/jvm/java-25-amazon-corretto

# 复制生产环境配置
cp "$SCRIPT_DIR/application-prod.properties" "$ROOT_DIR/backend/"

info "构建后端..."
if [ -f "./mvnw" ]; then
    ./mvnw clean package -DskipTests
else
    mvn clean package -DskipTests
fi
info "后端构建完成"

# ── [8/8] 配置服务 ─────────────────────────
step "[8/8] 配置 Nginx 和 Systemd"

# 安装 Nginx
if ! command -v nginx &> /dev/null; then
    info "安装 Nginx..."
    apt-get install -y nginx
fi

# 配置 Nginx
info "配置 Nginx..."
cp "$SCRIPT_DIR/nginx.conf" /etc/nginx/sites-available/indietracks.conf
ln -sf /etc/nginx/sites-available/indietracks.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-enabled/indietracks
nginx -t && systemctl reload nginx
info "Nginx 配置完成"

# 配置 Systemd
info "配置 Systemd 服务..."
cp "$SCRIPT_DIR/indietracks.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable indietracks
systemctl restart indietracks
info "Systemd 服务配置完成"

# 开放防火墙
info "配置防火墙..."
ufw allow 80/tcp 2>/dev/null || true
info "防火墙配置完成"

# ── 完成 ───────────────────────────────────
echo ""
echo "============================================"
echo "  部署完成！"
echo "============================================"
echo ""
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")
echo "  前端: http://$PUBLIC_IP"
echo "  后端 API: http://$PUBLIC_IP/api"
echo "  MinIO 控制台: http://$PUBLIC_IP:9001"
echo ""
echo "  查看后端状态: sudo systemctl status indietracks"
echo "  查看实时日志: sudo journalctl -u indietracks -f"
echo "  查看 MinIO 日志: tail -f $ROOT_DIR/logs/minio.log"
echo ""
echo "============================================"
