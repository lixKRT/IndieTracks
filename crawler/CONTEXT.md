# Crawler 领域术语表

## 数据实体

| 术语 | 说明 | DB 表 | 去重键 |
|:---|:---|:---|:---|
| Album | 专辑 | `albums` | `dizzylab_id` (VARCHAR) |
| Circle | 社团（同人社团/厂牌） | `circles` | `dizzylab_labelid` (INT) |
| User | 用户 | `users` | `dizzylab_user_id` (INT) |
| Tag | 标签 | `tags` | `name` (VARCHAR) |
| WorkFile | 曲目文件（试听音频） | `work_files` | 按 album_id 刷新 |
| Comment | 评论 | `comments` | (user_id, album_id, content) |

## 关联表

| 术语 | 说明 | DB 表 |
|:---|:---|:---|
| AlbumCircle | 专辑-社团关联 | `album_circles` |
| AlbumTag | 专辑-标签关联 | `album_tags` |
| UserCircle | 用户-社团成员关系 | `user_circles` |
| OwnedAlbum | 用户已购专辑 | `owned_albums` |
| Favorite | 用户收藏专辑 | `favorites` |
| CircleFollow | 用户关注社团 | `circle_follows` |

## 爬虫角色

| 术语 | 说明 |
|:---|:---|
| Staff | dizzylab 官方人员，角色不可降级 |
| Pro | 社团成员/创作者，由社团爬虫标记 |
| Normal | 普通用户，默认角色 |

## 架构模块

| 术语 | 说明 |
|:---|:---|
| Repository | 统一持久化层，所有 DB 读写 |
| ItemRegistry | Item 类型 → (resolve, upsert) 注册表 |
| DbSpiderMixin | 蜘蛛 DB 连接管理混入类 |
| StorageBackend | 文件存储抽象（MinIO / Memory） |
| DbConnection | 数据库连接上下文管理器 |
| Pipeline | Scrapy Pipeline，通过注册表调度 Item 写入 |

## 临时字段

Spider yield Item 时用 `_dizzylab_*` 前缀字段暂存外键引用，Pipeline 的 resolve 函数将其映射为 DB 主键：

- `_dizzylab_id` → `album_id`
- `_dizzylab_user_id` → `user_id`
- `_dizzylab_labelid` → `circle_id`
- `_tag_name` → `tag_id`
