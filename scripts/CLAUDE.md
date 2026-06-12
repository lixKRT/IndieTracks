# CLAUDE.md — Scripts

IndieTracks 运维脚本，分 Windows（Python）和 Linux（Bash）两套。

## 执行方式

### Windows

```bash
python scripts/windows/setup-database.py
python scripts/windows/setup-minio.py
python scripts/windows/run-crawlers.py
```

### Linux

```bash
bash scripts/linux/setup-all.sh          # 一键部署 Web 应用
bash scripts/linux/setup-crawler.sh      # 一键部署爬虫环境
bash scripts/linux/run-crawlers.sh       # 爬虫启动器
bash scripts/linux/deploy.sh             # 重新构建部署
bash scripts/linux/stop-all.sh           # 一键停止所有服务
```

## Linux 脚本说明

| 脚本 | 用途 | 前置条件 |
|:---|:---|:---|
| `setup-all.sh` | 一键部署 Web 应用（JDK+DB+MinIO+前端+后端+Nginx+Systemd） | Ubuntu 22.04+ |
| `setup-database.sh` | 安装 PostgreSQL + 建库建表 | — |
| `setup-minio.sh` | 下载 MinIO + 启动 + 建 bucket | — |
| `setup-crawler.sh` | 一键部署爬虫环境（venv+依赖+测试） | Python 3.11+ |
| `run-crawlers.sh` | 爬虫启动器（首次全量/增量更新） | venv 已创建 |
| `deploy.sh` | 重新构建前端+后端，重启服务 | 环境已部署 |
| `stop-all.sh` | 停止所有服务 + 清理进程 + 清理内存 | — |
| `build.sh` | 构建前端+后端 | 环境已部署 |
| `nginx.conf` | Nginx 配置模板 | — |
| `indietracks.service` | Systemd 服务配置 | — |
| `.env.example` | 环境变量模板 | — |

## Windows 脚本说明

| 脚本 | 用途 | 前置条件 |
|:---|:---|:---|
| `_common.py` | 共享工具库——find_psql、psql、read/write_json、run_scrapy、check_minio | Python 3.10+ |
| `setup-crawler.py` | **一键部署**——建 venv → 装依赖 → 配数据库 → 建表 → 检查 MinIO → 跑测试 | Python 3.11+ |
| `setup-database.py` | 5 步建库建表——找 psql → 填账号 → 测连接 → 执行 SQL → 可选清空 | PostgreSQL 已安装 |
| `setup-minio.py` | 5 步部署 MinIO——检查下载→启动(循环等 30s)→建 bucket→建用户→写配置 | — |
| `run-crawlers.py` | 爬虫启动器——5 项前置检查 → 首次全量 / 增量更新 | venv 已创建，PostgreSQL + MinIO 就绪 |

## `run-crawlers.sh` 流程

```
[Pre 1/5] 检查 venv
[Pre 2/5] 查找 psql
[Pre 3/5] 检查 database.json 账号密码（缺失则提示填写并保存）
[Pre 4/5] 测数据库连接 + 表存在（无表则调用 setup-database.sh）
[Pre 5/5] 检查 MinIO（未运行则调用 setup-minio.sh）

★ 首次爬取 (1)
  → full 模式
  → 输入 max_albums（默认 20）、max_users（默认 10）
  → 依次执行 album_bulk → album_incremental → circle → user_roles → user_pages
  → 最后询问是否全量刷新 (max=0)

★ 增量更新 (2)
  → incremental 模式
  → 输入 max_albums（默认 0=不限额）、max_users（默认 10）
  → 勾选要执行的爬虫（多选）
  → 依次执行
```

## Systemd 服务

`indietracks.service` 依赖：
- `postgresql.service`（必须）
- `minio.service`（必须）
- `nginx.service`（必须）

一键启动：`systemctl start indietracks`
一键停止：`systemctl stop indietracks` 或 `bash scripts/linux/stop-all.sh`

## 爬虫执行顺序

| 顺序 | 爬虫 | 用途 |
|:---|:---|:---|
| 1 | `album_bulk` (full, max=N) | 首批数据铺底 + 音频下载 |
| 2 | `album_incremental` | 日常追新 |
| 3 | `circle` | 社团描述+logo+成员ID |
| 4 | `user_roles` | 角色标记 |
| 5 | `user_pages` | 用户已购/收藏/关注 |
| 6 | `album_bulk` (full, max=0) | 最终全量刷新 |
