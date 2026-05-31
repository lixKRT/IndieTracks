#!/bin/bash
# ============================================
# 构建脚本 — 在本地或 CI 中运行
# ============================================
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "=== 1. 构建前端 ==="
cd "$PROJECT_ROOT/frontend"
npm ci
npm run build
echo "前端构建完成: frontend/dist/"

echo "=== 2. 构建后端 ==="
cd "$PROJECT_ROOT/backend"
./mvnw clean package -DskipTests
echo "后端构建完成: backend/target/backend-0.0.1-SNAPSHOT.jar"

echo "=== 构建完成 ==="
echo "产物:"
echo "  前端: $PROJECT_ROOT/frontend/dist/"
echo "  后端: $PROJECT_ROOT/backend/target/backend-0.0.1-SNAPSHOT.jar"
