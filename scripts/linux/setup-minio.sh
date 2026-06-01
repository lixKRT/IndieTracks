#!/bin/bash
# ============================================
# IndieTracks MinIO 部署脚本
# 下载 MinIO 二进制 + 建 bucket
# ============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TOOLS_DIR="$ROOT_DIR/tools"
MINIO_DIR="$TOOLS_DIR/minio"
MINIO_DATA="$ROOT_DIR/database/minio-data"
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
echo "  IndieTracks MinIO Setup"
echo "============================================"
echo ""

# ── [1/5] 加载环境变量 ─────────────────────
info "[1/5] 加载环境变量..."
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-minioadmin}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-minioadmin}"
MINIO_BUCKET="${MINIO_BUCKET:-indietracks}"

info "  Access Key: $MINIO_ACCESS_KEY"
info "  Bucket: $MINIO_BUCKET"
echo ""

# ── [2/5] 创建目录 ─────────────────────────
info "[2/5] 创建目录..."
mkdir -p "$MINIO_DIR"
mkdir -p "$MINIO_DATA"
info "  MinIO 目录: $MINIO_DIR"
info "  数据目录: $MINIO_DATA"
echo ""

# ── [3/5] 下载 MinIO ───────────────────────
info "[3/5] 下载 MinIO..."
MINIO_BIN="$MINIO_DIR/minio"

if [ -f "$MINIO_BIN" ]; then
    info "  MinIO 已存在，跳过下载"
else
    # 下载 MinIO Linux AMD64
    wget -q "https://dl.min.io/server/minio/release/linux-amd64/minio" -O "$MINIO_BIN"
    chmod +x "$MINIO_BIN"
    info "  MinIO 下载完成"
fi

# 下载 mc 客户端
MC_BIN="$MINIO_DIR/mc"
if [ -f "$MC_BIN" ]; then
    info "  mc 客户端已存在，跳过下载"
else
    wget -q "https://dl.min.io/client/mc/release/linux-amd64/mc" -O "$MC_BIN"
    chmod +x "$MC_BIN"
    info "  mc 客户端下载完成"
fi
echo ""

# ── [4/5] 启动 MinIO ───────────────────────
info "[4/5] 启动 MinIO..."

# 检查 MinIO 是否已在运行
if pgrep -x "minio" > /dev/null; then
    info "  MinIO 已在运行"
else
    # 后台启动 MinIO
    nohup "$MINIO_BIN" server "$MINIO_DATA" \
        --address ":9000" \
        --console-address ":9001" \
        > "$ROOT_DIR/logs/minio.log" 2>&1 &

    # 等待启动
    info "  等待 MinIO 启动..."
    for i in {1..30}; do
        if curl -s "http://localhost:9000" > /dev/null 2>&1; then
            info "  MinIO 启动成功"
            break
        fi
        sleep 1
    done

    if ! curl -s "http://localhost:9000" > /dev/null 2>&1; then
        error "  MinIO 启动超时"
    fi
fi
echo ""

# ── [5/5] 配置 mc 并创建 bucket ────────────
info "[5/5] 配置 mc 并创建 bucket..."

# 配置 mc alias
"$MC_BIN" alias set local http://localhost:9000 "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" 2>/dev/null || true

# 创建 bucket
if "$MC_BIN" ls "local/$MINIO_BUCKET" > /dev/null 2>&1; then
    info "  Bucket '$MINIO_BUCKET' 已存在"
else
    "$MC_BIN" mb "local/$MINIO_BUCKET"
    info "  Bucket '$MINIO_BUCKET' 创建完成"
fi

# 设置匿名访问（可选，用于公开访问）
"$MC_BIN" anonymous set download "local/$MINIO_BUCKET" 2>/dev/null || true
info "  已设置匿名下载权限"
echo ""

# ── 完成 ───────────────────────────────────
echo "============================================"
echo "  MinIO 部署完成！"
echo "  API 地址: http://localhost:9000"
echo "  控制台: http://localhost:9001"
echo "  Access Key: $MINIO_ACCESS_KEY"
echo "  Secret Key: $MINIO_SECRET_KEY"
echo "  Bucket: $MINIO_BUCKET"
echo "============================================"
echo ""
