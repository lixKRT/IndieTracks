#!/bin/bash
# ============================================
# 服务器部署脚本 — 在目标服务器上运行
# 前提: 已安装 JDK 21+, Nginx, PostgreSQL
# ============================================
set -e

APP_DIR="/opt/indietracks"
JAR_NAME="backend-0.0.1-SNAPSHOT.jar"

echo "=== 1. 创建目录 ==="
sudo mkdir -p "$APP_DIR"/{backend,frontend/dist,logs}

echo "=== 2. 部署后端 ==="
sudo cp backend/target/$JAR_NAME "$APP_DIR/backend/"
sudo cp scripts/linux/application-prod.properties "$APP_DIR/backend/"

echo "=== 3. 部署前端 ==="
sudo cp -r frontend/dist/* "$APP_DIR/frontend/dist/"

echo "=== 4. 配置 Nginx ==="
sudo cp scripts/linux/nginx.conf /etc/nginx/sites-available/indietracks.conf
sudo ln -sf /etc/nginx/sites-available/indietracks.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

echo "=== 5. 配置 Systemd 服务 ==="
sudo cp scripts/linux/indietracks.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable indietracks
sudo systemctl restart indietracks

echo "=== 6. 开放防火墙 ==="
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS (如果用)

echo "=== 部署完成 ==="
echo "检查状态: sudo systemctl status indietracks"
echo "查看日志: sudo journalctl -u indietracks -f"
echo "访问: http://$(hostname -I | awk '{print $1}')"
