#!/bin/bash
# ============================================
# IndieTracks 一键停止脚本
# 停止后端、Nginx、MinIO、PostgreSQL
# ============================================

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

echo "============================================"
echo "  IndieTracks 一键停止"
echo "============================================"
echo ""

# 停止后端
info "停止后端服务..."
systemctl stop indietracks 2>/dev/null && info "后端已停止" || warn "后端未运行"

# 停止 Nginx
info "停止 Nginx..."
systemctl stop nginx 2>/dev/null && info "Nginx 已停止" || warn "Nginx 未运行"

# 停止 MinIO
info "停止 MinIO..."
systemctl stop minio 2>/dev/null && info "MinIO 已停止" || warn "MinIO 未运行"
pkill -f "minio server" 2>/dev/null

# 停止 PostgreSQL
info "停止 PostgreSQL..."
systemctl stop postgresql 2>/dev/null && info "PostgreSQL 已停止" || warn "PostgreSQL 未运行"

# 清理残留进程
info "清理残留进程..."
pkill -f "backend-0.0.1-SNAPSHOT.jar" 2>/dev/null

# 清理内存缓存
info "清理内存缓存..."
sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null

echo ""
echo "============================================"
echo "  所有服务已停止"
echo "============================================"
echo ""
echo "  服务状态:"
echo "    indietracks: $(systemctl is-active indietracks 2>/dev/null || echo 'inactive')"
echo "    nginx:       $(systemctl is-active nginx 2>/dev/null || echo 'inactive')"
echo "    minio:       $(systemctl is-active minio 2>/dev/null || echo 'inactive')"
echo "    postgresql:  $(systemctl is-active postgresql 2>/dev/null || echo 'inactive')"
echo ""
