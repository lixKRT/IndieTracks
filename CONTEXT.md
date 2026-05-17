# IndieTracks 项目上下文

> 最后更新：2026-05-15（grill-with-docs 访谈 + P2 首页改造）

## 项目定位

**IndieTracks** 是一个独立音乐作品展示与试听平台，产品形态参考 Dizzylab（dizzylab.net）。支持专辑浏览、在线试听、社团展示、用户收藏等功能。

## 领域术语

| 术语 | 定义 |
|:---|:---|
| 专辑（Album） | 一组音乐作品的集合，由社团发布。包含标题、封面、价格、内容信息、曲目列表 |
| 社团（Circle） | 音乐创作团体，发布专辑。有成员列表（UserCircle 关联） |
| 用户（User） | 角色：`normal`（普通）或 `pro`（社团成员） |
| 曲目（WorkFile） | 专辑音轨。`file_type`：`preview`（试听）或 `full`（完整版） |
| 标签（Tag） | 专辑分类标记。专辑-标签多对多 |
| 收藏（Favorite） | 用户-专辑多对多 |
| 评论（Comment） | 用户对专辑的文本评价 |
| 专辑内容信息 | `info_title`（TEXT）和 `info_content`（TEXT）。爬虫原样入库，非必填 |

## 技术约定

- **字段命名**：全链路 snake_case。前端 Mock 数据 = 数据库列名 = 后端 JSON key
- **视觉风格**：暗色扁平（背景 `#0a0a0a`，主色 `#ff6b6b`）
- **前端**：Vue 3 + Vite 8 + Vue Router 4 + Axios + Pinia
- **后端**：Spring Boot 4 + Java 25 + JPA + Undertow
- **数据层**：PostgreSQL 18 + MinIO 对象存储
- **爬虫**：Scrapy，目标站 Dizzylab

### Dizzylab 目标页面

| 页面 | URL |
|:---|:---|
| 首页（专辑列表） | `https://www.dizzylab.net/` |
| 专辑详情 | `https://www.dizzylab.net/d/SW20/` |
| 社团列表 | `https://www.dizzylab.net/label/` |
| 社团详情 | `https://www.dizzylab.net/l/Static%20World/` |
| 用户已购专辑 | `https://www.dizzylab.net/u/72259/music/` |
| 用户收藏 | `https://www.dizzylab.net/u/72259/likes/` |
| 用户关注 | `https://www.dizzylab.net/u/72259/following/` |

## 数据模型要点

- 专辑由社团发布（`album_circles`），不由用户直接发布
- 专辑 `description` 已删除，替换为 `info_title` + `info_content`
- 价格筛选：`price = 0` / `price > 0`，不加枚举字段

## 前端架构要点

### 组件分层（原子化设计，无原子层）

```
molecules → organisms → layouts → views
```

### 页面清单（Mock 阶段）

| 路由 | 状态 |
|:---|:---|
| `/` 首页 | ✅ P2 完成 |
| `/album/:id` 专辑详情 | 🔨 P3 进行中 |
| `/labels` 社团列表 | ⬜ P5 |
| `/label/:id` 社团详情 | ⬜ P5 |
| `/tag` 分类浏览 | ⬜ P6 |
| `/user/:id` 用户页 | ⬜ 后期 |

### Pinia Store

- `player`：播放列表、当前曲目、播放/暂停、localStorage 持久化。不管理认证态。

### 播放器

- Spotify 风味底部播放条。可展开面板含曲目列表。与专辑详情曲目列表联动。

### 响应式

- 专辑网格：桌面 2 列（80% 宽，居中，列间距 5%），移动端 2 列
- 专辑卡片：桌面横版（60% 封面 + 40% 信息），移动端纵版（隐藏信息区）
- Navbar：≤768px 汉堡菜单

### 爬虫策略

分四个独立爬虫：专辑（首期 10 张）、社团人员、收藏、增量更新。合理延时。

## 已知问题

- AlbumGrid 外层容器宽度未达 80% 预期，内层 grid 居中逻辑需排查父级约束或 CSS 优先级。(2026-05-15)
