# IndieTracks 数据库 ER 图与 DDL

> 更新：2026-05-26
> PostgreSQL 18，14 张表

---

## 核心实体（4 张）

| 表 | 主键 | 去重键 | 说明 |
|:---|:---|:---|:---|
| `users` | `user_id` SERIAL | `dizzylab_user_id` UNIQUE | role: normal/pro/staff, `userpage_crawled_at` |
| `circles` | `circle_id` SERIAL | `dizzylab_labelid` UNIQUE | `member_count` 记录上次爬取成员数 |
| `albums` | `album_id` SERIAL | `dizzylab_id` UNIQUE | `info_title`/`info_content` 替代 description |
| `tags` | `tag_id` SERIAL | `name` UNIQUE | 标签（已去 `#`） |

## 关联表（6 张）

| 表 | 主键 | 说明 |
|:---|:---|:---|
| `user_circles` | (user_id, circle_id) | 社团成员 |
| `album_circles` | (album_id, circle_id) | 专辑-社团（多对多） |
| `album_tags` | (album_id, tag_id) | 专辑-标签（多对多） |
| `owned_albums` | (user_id, album_id) | 已购 |
| `favorites` | (user_id, album_id) | 收藏 |
| `circle_follows` | (user_id, circle_id) | 关注社团 |

## 数据表（3 张）

| 表 | 外键 | 说明 |
|:---|:---|:---|
| `work_files` | `album_id → albums` | 曲目，`file_type`: preview/full，`object_key` 存 MinIO 路径 |
| `comments` | `user_id → users` SET NULL, `album_id → albums` CASCADE | 评论 |
| `user_follows` | `user_id → users`, `followed_user_id → users` | 预留（dizzylab 无用户关注） |

## 关系图

```
users ──┬── owned_albums ──── albums
        ├── favorites ──────── albums
        ├── comments ───────── albums
        ├── user_circles ───── circles
        ├── circle_follows ─── circles
        └── user_follows ───── users (self-ref)

albums ──┬── work_files
         ├── album_tags ────── tags
         └── album_circles ─── circles
```

## 索引（14 条）

- `albums(dizzylab_id)` UNIQUE
- `users(dizzylab_user_id)` UNIQUE
- `circles(dizzylab_labelid)` UNIQUE
- `work_files(album_id)`, `work_files(file_type)`
- `comments(album_id)`
- `favorites(user_id)`
- `albums(publish_date)`
- `owned_albums(user_id)`, `owned_albums(album_id)`
- `circle_follows(user_id)`, `circle_follows(circle_id)`
- `user_follows(user_id)`, `user_follows(followed_user_id)`

## 迁移（幂等）

| 迁移 | 表 | 列 | 用途 |
|:---|:---|:---|:---|
| userpage_crawled_at | users | TIMESTAMP | user_pages 爬取追踪 |
| member_count | circles | INTEGER DEFAULT 0 | circle_members 成员数追踪 |

---

文件位置：`database/create_database.sql`
