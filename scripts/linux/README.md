# IndieTracks 部署指南

## 服务器要求

| 组件 | 最低版本 |
|------|---------|
| OS | Ubuntu 22.04+ / CentOS 8+ |
| JDK | 25 |
| Node.js | 20+ |
| PostgreSQL | 18 |
| Nginx | 1.22+ |
| MinIO | 最新版（自动下载） |

## 一键部署（推荐）

### 1. 配置环境变量

```bash
cd /root/IndieTracks/scripts/linux
cp .env.example .env
# 编辑 .env 文件，填写实际配置
```

### 2. 运行一键部署脚本

```bash
bash scripts/linux/setup-all.sh
```

脚本会自动完成：
- 安装 PostgreSQL 18 + 建库建表
- 下载 MinIO + 创建 bucket
- 构建前端（npm run build）
- 构建后端（mvn package）
- 配置 Nginx
- 配置 Systemd 服务
- 开放防火墙

## 手动部署

如果需要分步执行：

```bash
# 1. 安装数据库
bash scripts/linux/setup-database.sh

# 2. 安装 MinIO
bash scripts/linux/setup-minio.sh

# 3. 部署应用
bash scripts/linux/deploy.sh
```

## 目录结构

```
/root/IndieTracks/
├── frontend/dist/          ← Nginx 静态文件
├── backend/target/         ← JAR 包
├── tools/minio/            ← MinIO 二进制
├── database/minio-data/    ← MinIO 数据
├── logs/                   ← 日志
└── scripts/linux/          ← 部署脚本
    ├── .env                ← 环境变量
    ├── setup-all.sh        ← 一键部署
    ├── setup-database.sh   ← 数据库部署
    ├── setup-minio.sh      ← MinIO 部署
    ├── deploy.sh           ← 应用部署
    ├── nginx.conf          ← Nginx 配置模板
    └── indietracks.service ← Systemd 服务配置
```

## 环境变量说明

在 `scripts/linux/.env` 中配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DB_HOST` | 数据库地址 | `localhost` |
| `DB_PORT` | 数据库端口 | `5432` |
| `DB_NAME` | 数据库名 | `indietracks` |
| `DB_USER` | 数据库用户 | `postgres` |
| `DB_PASS` | 数据库密码 | `postgres` |
| `JWT_SECRET` | JWT 密钥（≥32字符） | — |
| `MINIO_ENDPOINT` | MinIO 地址 | `http://localhost:9000` |
| `MINIO_ACCESS_KEY` | MinIO 用户名 | `minioadmin` |
| `MINIO_SECRET_KEY` | MinIO 密码 | `minioadmin` |
| `MINIO_BUCKET` | MinIO 桶名 | `indietracks` |

## 常用命令

```bash
# 查看后端状态
sudo systemctl status indietracks

# 查看实时日志
sudo journalctl -u indietracks -f

# 重启后端
sudo systemctl restart indietracks

# 查看 MinIO 日志
tail -f /root/IndieTracks/logs/minio.log

# 检查端口
sudo ss -tlnp | grep -E '80|8080|9000'
```

## 访问

部署完成后，浏览器访问 `http://你的服务器IP` 即可。

- 前端：http://localhost
- 后端 API：http://localhost/api
- MinIO 控制台：http://localhost:9001

## 阿里云安全组

如果使用阿里云服务器，需要在控制台手动开放端口：

| 端口 | 协议 | 用途 |
|------|------|------|
| 80 | TCP | HTTP 访问 |
| 9000 | TCP | MinIO API（可选） |
| 9001 | TCP | MinIO 控制台（可选） |
