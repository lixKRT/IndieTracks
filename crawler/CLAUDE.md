# CLAUDE.md — Crawler

IndieTracks Scrapy 爬虫项目，采集 dizzylab.net 数据。

## 命令

```bash
cd crawler
.\env\Scripts\activate                   # 激活 venv (Windows)

# 建表 / 迁移
python setup_db.py                       # 执行 database/create_database.sql

# 爬虫运行
scrapy crawl album_test                  # 测试爬虫（10 张专辑，调试用）
scrapy crawl album_bulk                  # 批量爬虫（遵守 spider.json）
scrapy crawl album_incremental           # 增量爬虫（永远增量，不受 spider.json 控制）
scrapy crawl circle                      # 社团爬虫（描述+logo+成员ID）
scrapy crawl user_roles                  # 用户角色爬虫 /setup
scrapy crawl user_pages                  # 用户维页面（DB 读取，默认 20 人）
scrapy crawl user_pages -a user_ids=2,3  # 用户维页面（指定用户）

# 单元测试
python -m pytest tests/ -v               # 运行全部测试（195 个）
```

## 配置文件 (`crawler/config/`)

| 文件 | 用途 | 关键字段 |
|:---|:---|:---|
| `database.json` | PG 连接 | host/port/database/user/password |
| `spider.json` | 爬虫行为控制 | `mode` (full/incremental), `max_albums` (50), `max_users` (10) |
| `delay.json` | 延迟策略 | `download_delay`, `between_albums_min/random`, `between_tracks_min/random_max` |
| `minio.json` | MinIO 连接 | endpoint/access_key/secret_key/bucket/prefixes |

**spider.json 适用范围：** `album_bulk`, `circle`, `user_roles`, `user_pages`
**例外：** `album_incremental`（永远增量+不限额）、`album_test`（固定 10 张）

## 项目结构

```
crawler/
├── config/
│   ├── delay.json
│   ├── database.json
│   ├── spider.json
│   └── minio.json
├── indietracks_spider/
│   ├── items.py              # 12 个 Scrapy Item（含临时关联字段 _dizzylab_*）
│   ├── pipelines.py          # PostgreSQL Pipeline（注册表调度 + 计数汇总）
│   ├── repository.py         # 统一持久化层（FK 缓存 + Upsert + 直接 SQL 操作）
│   ├── item_registry.py      # Item 注册表（resolve + upsert 函数注册）
│   ├── db_mixin.py           # DbSpiderMixin（统一 DB 连接管理）
│   ├── settings.py           # 延迟加载 config JSON
│   ├── utils/
│   │   ├── config_loader.py  # get_delay/spider/database/minio_config() + 测试注入
│   │   ├── constants.py      # BASE, API_DISCS, PAGE_SIZE, TRACK_RE
│   │   ├── db.py             # DbConnection 上下文管理器 + 旧接口兼容
│   │   ├── delay.py          # schedule_album_delay(), schedule_track_delay(), schedule_circle_delay()
│   │   ├── storage.py        # StorageBackend 抽象 + MinioBackend + MemoryBackend
│   │   ├── circle.py         # extract_circle_info(), yield_circle_members()
│   │   ├── minio.py          # 向后兼容代理 → storage.py
│   │   └── parsing.py        # safe_json_load, check_response_ok, extract_user_id 等
│   └── spiders/
│       ├── album_base.py     # 专辑爬虫基类（make_disc_request + _parse_discs_response）
│       ├── album_test.py     # 测试爬虫（10 张专辑）
│       ├── album_bulk.py     # 批量爬虫（reactor.callLater 非阻塞延迟）
│       ├── album_incremental.py # 增量爬虫（遇完整专辑即停）
│       ├── circle.py         # 社团爬虫（_pop_next_circle 队列驱动）
│       ├── user_roles.py     # STAFF/PRO 角色（PRO xpath 有上界）
│       └── user_pages.py     # 用户已购/收藏/关注（自动建占位行）
├── tests/                    # 单元测试（195 个用例）
│   ├── conftest.py           # 共享 fixtures
│   ├── test_album_base.py    # make_disc_request + _parse_discs_response
│   ├── test_album_complete.py
│   ├── test_circle_utils.py
│   ├── test_config_loader.py
│   ├── test_constants.py
│   ├── test_db.py            # DbConnection 全生命周期
│   ├── test_db_mixin.py
│   ├── test_delay.py
│   ├── test_item_registry.py
│   ├── test_items.py
│   ├── test_parsing.py
│   ├── test_pipelines.py
│   ├── test_repository.py    # Repository 全部方法
│   └── test_storage.py       # MinioBackend + MemoryBackend
├── tool/
│   └── get_url.py            # 网页源码获取工具
├── requirements.txt          # scrapy + psycopg2-binary + minio
├── scrapy.cfg
└── setup_db.py
```

## 架构分层

```
Spider (解析 HTML → yield Item)
  │
  ├── DbSpiderMixin → DbConnection → Repository（蜘蛛直写：update_role, mark_user_crawled 等）
  │
  └── Pipeline → item_registry（resolve + upsert）→ Repository（Item 写入）
```

### 核心模块职责

| 模块 | 职责 | 接口深度 |
|:---|:---|:---|
| `Repository` | 所有 DB 读写，FK 缓存，upsert，直接 SQL 操作 | 深（一个类覆盖 13 张表） |
| `item_registry` | Item 类型 → (resolve_fn, upsert_fn) 注册表 | 深（新增 Item 只需 register） |
| `DbSpiderMixin` | 蜘蛛 DB 连接懒初始化 + 统一清理 | 深（4 个蜘蛛共用） |
| `StorageBackend` | 文件存储抽象（MinIO 生产 / Memory 测试） | 深（可替换后端） |
| `DbConnection` | 数据库连接上下文管理器，支持 config 注入 | 深（测试无需真实 DB） |

## 爬虫设计

### album_bulk — 批量爬虫（主要爬虫）

**用途：** 首次铺底 + 全量刷新。遵守 spider.json（mode + max_albums）。

**控制逻辑：**

| mode | 数据完整的专辑 | 空壳专辑（info_title IS NULL） |
|:---|:---|:---|
| `full` | 重爬（计入 max_albums） | 重爬（计入 max_albums） |
| `incremental` | 跳过 | **不跳过**，视为未完整爬取 |

**流程（parse_album_detail，继承自 BaseAlbumSpider）：**
1. 构造 AlbumItem → yield
2. 遍历曲目 `<li data-audio="...">` → `storage.upload_audio()` → yield WorkFileItem
3. 曲目间延迟：`between_tracks_min + rand(0, between_tracks_random_max)` 秒
4. 解析 Tag → yield TagItem + AlbumTagItem
5. 解析 Circle → yield CircleItem + AlbumCircleItem
6. yield 子请求：buyers → comments → circle_detail
7. 专辑间延迟：`reactor.callLater` 调度下一张（不阻塞）

**album_bulk / album_incremental / album_test 均继承 BaseAlbumSpider，共享解析逻辑。**

### album_incremental — 增量爬虫

- 从 API 第一页（`l=0`）开始
- 遇到第一条 **数据完整**（info_title IS NOT NULL）的专辑立即停止
- 永远增量+不限额，不受 spider.json 控制

### circle — 社团爬虫

- `_pop_next_circle()` 从队列取出下一个社团，返回 Request
- `start()` yield 第一个请求，后续通过 `_on_delay_done` → `engine.crawl()` 注入
- `full`: 全部重爬 / `incremental`: 比较 `circles.member_count` 与 `user_circles` 行数，一致则跳过
- 异常保护：DB 写入失败不阻塞延迟回调

### user_roles — 用户角色

- 爬 `/setup`，解析 STAFF / PRO 区域
- PRO xpath 有上界（遇到下一个 h2 即停止），不会溢出到后续区域
- `full`: 全部 UPDATE role / `incremental`: 仅 UPDATE role 为空或 normal 的用户
- 通过 Repository.update_role() 写入，staff 不可降级

### user_pages — 用户维页面

- 3 个页面：`/u/{id}/music/` → owned_albums, `/u/{id}/likes/` → favorites, `/u/{id}/following/` → circle_follows
- 用户来源：`-a user_ids=` 或 DB 读取（incremental 跳过 30 天内已爬）
- `resolve_album_id` / `resolve_circle_id_by_name` 查不到时自动建占位行
- 通过 Repository 写入，不走 Pipeline

## Pipeline 写入策略

Pipeline 使用 `item_registry` 注册表调度，不再有 isinstance 链：

| 步骤 | 表 | 去重方式 |
|:---|:---|:---|
| 1 | `tags` | `ON CONFLICT (name) DO UPDATE ... RETURNING tag_id` |
| 2 | `circles` | `ON CONFLICT (dizzylab_labelid) DO UPDATE ... RETURNING circle_id` |
| 3 | `users` | `ON CONFLICT (dizzylab_user_id) DO UPDATE ...`（role 保护：staff 不可降级） |
| 4 | `albums` | `ON CONFLICT (dizzylab_id) DO UPDATE ... RETURNING album_id`（info_title/content/publish_date COALESCE 保护） |
| 5 | `album_tags` | `ON CONFLICT DO NOTHING` |
| 6 | `album_circles` | `ON CONFLICT DO NOTHING` |
| 7 | `work_files` | `DELETE + INSERT`（按 album_id 清旧数据） |
| 8 | `comments` | `ON CONFLICT (user_id, album_id, content) DO NOTHING` |
| 9 | `owned_albums` | `ON CONFLICT DO NOTHING` |
| 10 | `favorites` | `ON CONFLICT DO NOTHING` |
| 11 | `user_circles` | `ON CONFLICT DO NOTHING` |
| 12 | `circle_follows` | `ON CONFLICT DO NOTHING` |

**FK 解析：** `item_registry` 的 resolve 函数将 `_dizzylab_id` / `_dizzylab_user_id` / `_dizzylab_labelid` / `_tag_name` 临时字段通过 Repository 缓存映射为 DB 主键。解析失败时 `logger.warning` 警告（不再静默 None）。

**写入汇总：** Pipeline 关闭时打印 `Pipeline 写入汇总: AlbumItem=50 | WorkFileItem=320 | ...`

## 错误处理

- `safe_json_load(response)` — JSON 解析失败返回 None + log warning
- `check_response_ok(response)` — HTTP 400+ 返回 False（3xx 不阻断，429 返回 False 由 retry 处理）
- `float(price)` — 非数字价格回退 0.0，不崩溃
- Pipeline 异常 → rollback + 返回 None（item 丢弃）+ log error
- circle 爬虫 `_on_delay_done` — 异常保护，失败后仍尝试继续
- circle 爬虫 `parse_circle_detail` — DB 写入失败不阻塞延迟回调注册

## 测试

```bash
cd crawler
.\env\Scripts\activate
python -m pytest tests/ -v               # 195 个用例
python -m pytest tests/test_repository.py # Repository 单独测试
```

测试使用：
- `MemoryBackend` 替代 MinIO（无需真实服务）
- `DbConnection(config={...})` 注入配置（无需真实数据库）
- `set_config_override()` / `clear_config_overrides()` 注入配置
- `clear_registry()` / `register_builtins()` 重置注册表
