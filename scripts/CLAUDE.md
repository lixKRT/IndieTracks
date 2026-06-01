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
```

## 脚本说明

| 脚本 | 用途 | 前置条件 |
|:---|:---|:---|
| `_common.py` | 共享工具库——find_psql、psql、read/write_json、run_scrapy、check_minio | Python 3.10+ |
| `setup-crawler.py` | **一键部署**——建 venv → 装依赖 → 配数据库 → 建表 → 检查 MinIO → 跑测试 | Python 3.11+ |
| `setup-database.py` | 5 步建库建表——找 psql → 填账号 → 测连接 → 执行 SQL → 可选清空 | PostgreSQL 已安装 |
| `setup-minio.py` | 5 步部署 MinIO——检查下载→启动(循环等 30s)→建 bucket→建用户→写配置 | — |
| `run-crawlers.py` | 爬虫启动器——5 项前置检查 → 首次全量 / 增量更新 | venv 已创建，PostgreSQL + MinIO 就绪 |

## `run-crawlers.py` 流程

```
[Pre 1/5] 检查 venv
[Pre 2/5] 查找 psql
[Pre 3/5] 检查 database.json 账号密码（缺失则提示填写并保存）
[Pre 4/5] 测数据库连接 + 表存在（无表则调用 setup-database.py）
[Pre 5/5] 检查 MinIO（未运行则调用 setup-minio.py）

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

## `_common.py` 关键函数

| 函数 | 说明 |
|:---|:---|
| `find_psql()` | 查找 psql.exe：命令 → 默认路径(17/16/15) → 用户输入。结果缓存 |
| `psql(*args, password="")` | 执行 psql。password 非空则设 PGPASSWORD 环境变量 |
| `read_json(path)` | 安全读 JSON，文件不存在返回 `{}` |
| `write_json(path, data)` | 安全写 JSON（自动建目录） |
| `run_scrapy(spider)` | 用 venv Python 执行 scrapy crawl，Ctrl+C 返回 2 |
| `check_minio()` | HTTP GET localhost:9000 检测 MinIO |

## 爬虫执行顺序

| 顺序 | 爬虫 | 用途 |
|:---|:---|:---|
| 1 | `album_bulk` (full, max=N) | 首批数据铺底 + 音频下载 |
| 2 | `album_incremental` | 日常追新 |
| 3 | `circle` | 社团描述+logo+成员ID |
| 4 | `user_roles` | 角色标记 |
| 5 | `user_pages` | 用户已购/收藏/关注 |
| 6 | `album_bulk` (full, max=0) | 最终全量刷新 |

## 架构说明

### Pipeline（重构版）

Pipeline 使用 `item_registry` 注册表调度，不再有 isinstance 链：
- 新增 Item 只需在 `items.py` 定义 + `item_registry.register()`
- FK 解析失败时 `logger.warning` 警告（不再静默 None）
- 关闭时打印写入汇总：`Pipeline 写入汇总: AlbumItem=50 | WorkFileItem=320 | ...`

### Repository（统一持久化层）

所有 DB 操作通过 `repository.py`：
- FK 缓存：`_album_id_cache` / `_circle_id_cache` / `_user_id_cache` / `_tag_id_cache`
- Upsert：`upsert_album()` / `upsert_user()` 等 12 种
- 直接 SQL：`update_role()` / `mark_user_crawled()` / `is_user_page_fresh()` 等
- 蜘蛛直写：`user_pages` / `user_roles` / `circle` 通过 Repository 直接写 DB

### 存储后端

`storage.py` 提供 `StorageBackend` 抽象：
- `MinioBackend` — 生产环境，下载 CDN 文件 + 上传 MinIO
- `MemoryBackend` — 测试用，不发起真实 HTTP 请求
- 向后兼容：`minio.py` 代理到 `storage.py`

### 延迟控制（统一走 `utils/delay.py`）

| 函数 | 用途 | 阻塞 |
|:---|:---|:---|
| `schedule_album_delay(min, rand, callback)` | 专辑间延迟 | 不阻塞（reactor.callLater） |
| `schedule_track_delay(min, rand)` | 曲目间延迟 | 阻塞（time.sleep，因下载已阻塞） |
| `schedule_circle_delay(delay, callback)` | 社团间延迟 | 不阻塞（reactor.callLater） |

### 社团详情解析（共享函数）

`utils/circle.py` 提供社团详情页解析，供 `circle.py` 和 `album_base.py` 复用：

| 函数 | 功能 | 返回 |
|:---|:---|:---|
| `extract_circle_info(response)` | 提取描述 + logo | `(description, logo_key)` |
| `yield_circle_members(response, labelid)` | 解析成员列表 | yield `UserItem`(role=pro) + `UserCircleItem` |

### MinIO 文件下载

| 资源类型 | MinIO 前缀 | 自动识别规则 | 调用位置 |
|:---|:---|:---|:---|
| 专辑封面 | `covers/` | URL 含 `/media/cover/` | `album_base.py::parse_album_detail` |
| 社团 logo | `logos/` | URL 含 `/media/label_cover/` | `album_base.py::parse_circle_detail`，`circle.py::parse_circle_detail` |
| 用户头像 | `avatars/` | URL 含 `/media/avatars/` | `album_base.py::parse_buyers/comments`，`user_pages.py::parse_music` |
| 试听音频 | `audio/preview/` | 固定前缀 | `album_base.py::parse_album_detail` |
