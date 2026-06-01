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
├── crawler/                ← 爬虫项目
│   ├── env/                ← Python venv
│   ├── config/             ← 爬虫配置
│   └── indietracks_spider/ ← 爬虫代码
├── tools/minio/            ← MinIO 二进制
├── database/minio-data/    ← MinIO 数据
├── logs/                   ← 日志
└── scripts/linux/          ← 部署脚本
    ├── .env                ← 环境变量
    ├── setup-all.sh        ← 一键部署（Web 应用）
    ├── setup-crawler.sh    ← 一键部署（爬虫）
    ├── setup-database.sh   ← 数据库部署
    ├── setup-minio.sh      ← MinIO 部署
    ├── deploy.sh           ← 应用部署
    ├── run-crawlers.sh     ← 爬虫启动器
    ├── nginx.conf          ← Nginx 配置模板
    └── indietracks.service ← Systemd 服务配置
```

## 爬虫部署

### 一键部署爬虫

```bash
bash scripts/linux/setup-crawler.sh
```

脚本会自动完成：
- 检查 Python 版本（需要 3.11+）
- 创建 venv + 安装依赖
- 配置 database.json
- 测试数据库连接 + 建表
- 检查 MinIO
- 运行单元测试验证

### 运行爬虫

```bash
# 使用爬虫启动器（推荐）
bash scripts/linux/run-crawlers.sh

# 或手动运行
cd /root/IndieTracks/crawler
source env/bin/activate
scrapy crawl album_bulk
```

### 爬虫启动器功能

`run-crawlers.sh` 提供两种模式：

**首次爬取（full 模式）：**
- 依次运行所有爬虫：album_bulk → album_incremental → circle → user_roles → user_pages
- 可配置最大爬取专辑数和用户数

**增量更新（incremental 模式）：**
- 选择要运行的爬虫
- 支持单个或多个爬虫同时运行

### 爬虫配置

编辑 `crawler/config/spider.json`：

```json
{
  "mode": "full",
  "max_albums": 24,
  "max_users": 10
}
```

| 字段 | 说明 |
|------|------|
| `mode` | `full`（全量）或 `incremental`（增量） |
| `max_albums` | 最大爬取专辑数（0=不限） |
| `max_users` | 最大爬取用户数（0=不限） |

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
