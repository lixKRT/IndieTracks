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
scrapy crawl circle_members              # 社团成员爬虫
scrapy crawl user_roles                  # 用户角色爬虫 /setup
scrapy crawl user_pages                  # 用户维页面（DB 读取，默认 20 人）
scrapy crawl user_pages -a user_ids=2,3  # 用户维页面（指定用户）
```

## 配置文件 (`crawler/config/`)

| 文件 | 用途 | 关键字段 |
|:---|:---|:---|
| `database.json` | PG 连接 | host/port/database/user/password |
| `spider.json` | 爬虫行为控制 | `mode` (full/incremental), `max_albums` (50), `max_users` (20) |
| `delay.json` | 延迟策略 | `download_delay`, `between_albums_min/random`, `between_tracks_min/random_max` |
| `minio.json` | MinIO 连接 | endpoint/access_key/secret_key/bucket/prefixes |

**spider.json 适用范围：** `album_bulk`, `circle_members`, `user_roles`, `user_pages`
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
│   ├── items.py              # 14 个 Scrapy Item（含临时关联字段 _dizzylab_*）
│   ├── pipelines.py          # PostgreSQL Pipeline（upsert + ID 缓存 + 13 种 item）
│   ├── settings.py           # 动态加载 config JSON
│   ├── utils/
│   │   ├── config_loader.py  # get_delay/spider/database/minio_config()
│   │   ├── constants.py      # BASE, API_DISCS, PAGE_SIZE, TRACK_RE
│   │   ├── db.py             # get_connection(), close_connection()
│   │   ├── delay.py          # between_albums_sleep(), between_tracks_sleep()
│   │   ├── minio.py          # download_and_upload() — CDN 下载 + MinIO 上传
│   │   └── parsing.py        # extract_user_id, parse_date_cn, parse_track_title, safe_json_load, check_response_ok
│   └── spiders/
│       ├── album_base.py         # 专辑爬虫基类（共享 parse 方法 + _album_is_complete）
│       ├── album_test.py         # 测试爬虫（10 张专辑）
│       ├── album_bulk.py         # 批量爬虫（reactor.callLater 非阻塞延迟）
│       ├── album_incremental.py  # 增量爬虫（遇完整专辑即停）
│       ├── circle_members.py     # 社团成员（member_count 精确跳过 + reactor 延迟）
│       ├── user_roles.py         # STAFF/PRO 角色
│       └── user_pages.py         # 用户已购/收藏/关注社团
├── tool/
│   └── get_url.py            # 网页源码获取工具
├── requirements.txt          # scrapy + psycopg2-binary + minio
├── scrapy.cfg
└── setup_db.py
```

## 爬虫设计

### album_bulk — 批量爬虫（主要爬虫）

**用途：** 首次铺底 + 全量刷新。遵守 spider.json（mode + max_albums）。

**控制逻辑：**

| mode | 数据完整的专辑 | 空壳专辑（info_title IS NULL） |
|:---|:---|:---|
| `full` | 重爬（计入 max_albums） | 重爬（计入 max_albums） |
| `incremental` | 跳过 | **不跳过**，视为未完整爬取 |

**架构：** 队列驱动 + reactor 延迟。

```
start_requests → API 首页
parse_disc_list → 入队列 _pending_discs
_schedule_next → crawler.engine.crawl() 注入单张专辑
parse_album_detail (BaseAlbumSpider) → 解析 + 音频下载
_after_album_detail → reactor.callLater(wait, _schedule_next) ← 不阻塞 reactor
队列空 → 自动翻页
增量模式整页跳过 → 停止
```

**流程（parse_album_detail，继承自 BaseAlbumSpider）：**
1. 构造 AlbumItem → yield
2. 遍历曲目 `<li data-audio="...">` → `download_and_upload()` → yield WorkFileItem
3. 曲目间延迟：`between_tracks_min + rand(0, between_tracks_random_max)` 秒（time.sleep，CDN 下载同步阻塞）
4. 解析 Tag → yield TagItem + AlbumTagItem
5. 解析 Circle → yield CircleItem + AlbumCircleItem
6. yield 子请求：buyers → comments → circle_detail
7. 专辑间延迟：`reactor.callLater` 调度下一张（不阻塞）

**album_bulk / album_incremental / album_test 均继承 BaseAlbumSpider，共享解析逻辑。**

### album_incremental — 增量爬虫

- 从 API 第一页（`l=0`）开始
- 遇到第一条 **数据完整**（info_title IS NOT NULL）的专辑立即停止
- 永远增量+不限额，不受 spider.json 控制

### circle_members — 社团成员

- 队列驱动 + reactor.callLater 延迟（不阻塞引擎）
- `full`: 全部重爬 / `incremental`: 比较 `circles.member_count` 与 `user_circles` 行数，一致则跳过
- 爬完后 `UPDATE circles SET member_count = {found}`

### user_roles — 用户角色

- 爬 `/setup`，解析 STAFF / PRO 区域
- `full`: 全部 UPDATE role / `incremental`: 仅 UPDATE role 为空或 normal 的用户
- 直接 DB UPDATE，不走 Pipeline。HTTP 非 2xx 则 CloseSpider

### user_pages — 用户维页面

- 3 个页面：`/u/{id}/music/` (`?page=N`) → owned_albums, `/u/{id}/likes/` (`?dp=N`) → favorites, `/u/{id}/following/` (`?dp=N`) → circle_follows
- 用户来源：`-a user_ids=` 或 DB 读取（incremental 跳过 30 天内已爬）
- 专辑 ID 在 spider 内通过 DB 直接查（不存在的建占位行），社团 ID 同理

## Pipeline 写入策略

| 步骤 | 表 | 去重方式 |
|:---|:---|:---|
| 1 | `tags` | `ON CONFLICT (name) DO UPDATE ... RETURNING tag_id` |
| 2 | `circles` | `ON CONFLICT (dizzylab_labelid) DO UPDATE ... RETURNING circle_id` |
| 3 | `users` | `ON CONFLICT (dizzylab_user_id) DO UPDATE ...`（role 保护：staff 不可降级） |
| 4 | `albums` | `ON CONFLICT (dizzylab_id) DO UPDATE ... RETURNING album_id`（info_title/content/publish_date COALESCE 保护） |
| 5 | `album_tags` | `ON CONFLICT DO NOTHING` |
| 6 | `album_circles` | `ON CONFLICT DO NOTHING` |
| 7 | `work_files` | `DELETE + INSERT`（按 album_id 清旧数据） |
| 8 | `comments` | 直接 INSERT |
| 9 | `owned_albums` | `ON CONFLICT DO NOTHING` |
| 10 | `favorites` | `ON CONFLICT DO NOTHING` |
| 11 | `user_circles` | `ON CONFLICT DO NOTHING` |
| 12 | `circle_follows` | `ON CONFLICT DO NOTHING` |
| 13 | `user_follows` | `ON CONFLICT DO NOTHING`（预留，dizzylab 无此功能） |

**临时字段解析：** Pipeline `_resolve_refs` 将 `_dizzylab_id` / `_dizzylab_user_id` / `_dizzylab_labelid` / `_tag_name` 等临时字段通过内存缓存映射为 DB 主键。所有临时字段已在 `items.py` 中定义。

## 错误处理

所有 parse 回调统一使用 `utils/parsing.py` 中的两个保护函数：

- `safe_json_load(response)` — JSON 解析失败返回 None + log warning（不会崩溃）
- `check_response_ok(response)` — HTTP ≥400 返回 False + log warning

覆盖范围：
- `parse_disc_list` × 3（album_bulk/incremental/test）— JSON + HTTP
- `parse_buyers` / `parse_comments`（BaseAlbumSpider）— JSON + HTTP
- `parse_setup`（user_roles）— HTTP（失败 CloseSpider）
- `parse_circle_detail`（circle_members）— HTTP（失败跳过，继续下一个）
- `parse_music/likes/following` × 3（user_pages）— HTTP（失败跳过）

## MinIO 音频下载

`utils/minio.py::download_and_upload(cdn_url, album_slug, sort_order)` 在 BaseAlbumSpider.parse_album_detail 中被调用：

1. `requests.get()` 从 CDN 下载 MP3
2. `minio.put_object()` 上传到 MinIO
3. 返回 `(object_key, file_size)` — 失败返回 None 则跳过该曲目

**命名：** `audio/preview/{album_slug}/{sort_order:03d}.mp3`

**前置条件：** MinIO 服务必须先启动（`scripts/windows/setup-minio.bat`）。

## 数据库

### 14 张表

- `users` — dizzylab_user_id UNIQUE, role: normal/pro/staff, `userpage_crawled_at`
- `circles` — dizzylab_labelid UNIQUE, `member_count` 成员数追踪
- `user_circles` — 用户-社团（多对多）
- `albums` — dizzylab_id UNIQUE, info_title + info_content 替代 description
- `album_circles` — 专辑-社团（多对多）
- `work_files` — 曲目, file_type: preview/full, object_key 存 MinIO 路径
- `tags` / `album_tags` — 标签分类（多对多）
- `comments` — 评论
- `favorites` — 收藏（多对多）
- `owned_albums` — 已购（多对多）
- `circle_follows` — 关注社团（多对多）
- `user_follows` — 关注用户（多对多，预留）

所有表用 SERIAL PK。唯一索引：dizzylab_id / dizzylab_user_id / dizzylab_labelid。

### 初始化

```bash
psql -U postgres -d indietracks -f database/create_database.sql   # 建表 + 幂等迁移
psql -U postgres -d indietracks -f database/init.sql              # 清空数据 + 重置序列
```

## 爬虫执行优先级

| 顺序 | 爬虫 | 前置条件 | 用途 |
|:---|:---|:---|:---|
| 1 | `album_bulk`（full, max=50） | MinIO 已启动 | 首批数据铺底 + 音频下载 |
| 2 | `album_incremental` | 首期数据已有 | 日常追新 |
| 3 | `circle_members` | circles 表有数据 | 社团成员补充 |
| 4 | `user_roles` | users 表有数据 | 角色标记 |
| 5 | `user_pages` | users/albums/circles 有数据 | 用户已购/收藏/关注 |
| 6 | `album_bulk`（full, max=0） | MinIO 已启动 | 最终全量刷新 |
