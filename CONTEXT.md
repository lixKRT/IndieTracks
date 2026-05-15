# IndieTracks 项目上下文

> 最后更新：2026-05-15（首次访谈，grill-with-docs）

## 项目定位

**IndieTracks** 是一个独立音乐作品展示与试听平台，产品形态参考 Dizzylab（dizzylab.net），但为独立产品。支持专辑浏览、在线试听、社团展示、用户收藏等功能。

## 领域术语

| 术语 | 定义 |
|:---|:---|
| **专辑（Album）** | 一组音乐作品的集合，由社团发布。包含标题、封面、价格、内容信息、曲目列表等。 |
| **社团（Circle）** | 音乐创作团体，发布专辑。一个社团有多名成员（UserCircle 关联）。 |
| **用户（User）** | 平台使用者。角色分 `normal`（普通用户）和 `pro`（社团成员）。 |
| **曲目（WorkFile）** | 专辑内的一首音乐文件。区分 `preview`（试听）和 `full`（完整版）。 |
| **标签（Tag）** | 专辑分类标记，如"东方project"、"电子音乐"。专辑和标签多对多。 |
| **收藏（Favorite）** | 用户收藏专辑。用户-专辑多对多。 |
| **评论（Comment）** | 用户对专辑的文字评价。 |
| **专辑内容信息** | 专辑页面上展示的富文本信息区块，包含标题（`info_title`）和正文（`info_content`），可能含曲目列表、外链、简介等。（爬取自目标站，非必填） |

## 技术约定

- **字段命名**：全链路 snake_case。前端 Mock 数据、后端 JSON 序列化、数据库列名三者一致。后端 Spring Boot 不配置 camelCase 转换，前端不写 key 映射拦截器。
- **视觉风格**：暗色扁平主题（深色背景 `#0a0a0a`，主色调 `#ff6b6b`），非拟态风格。
- **数据层**：PostgreSQL 18，MinIO 对象存储。
- **前端**：Vue 3 + Vite 8 + Vue Router 4 + Axios + Pinia。
- **后端**：Spring Boot 4 + Java 25 + Spring Data JPA + Undertow。
- **爬虫**：Scrapy，目标站 Dizzylab。

## 数据模型要点

- 专辑由社团发布（`album_circles` 多对多关联表），不由用户直接发布。
- 用户通过 `user_circles` 关联社团，`user_role = 'pro'` 表示社团成员。
- 专辑内容信息拆为 `info_title`（TEXT）和 `info_content`（TEXT）两个字段，爬虫原样入库。
- 价格筛选通过 `price = 0` / `price > 0` 判断，不加枚举字段。

## 前端页面清单（Mock 阶段）

| 路由 | 页面 | 说明 |
|:---|:---|:---|
| `/` | 首页（作品列表） | 专辑卡片网格，标签筛选 |
| `/album/:id` | 专辑详情页 | 封面、信息、曲目列表、评论区、购买 |
| `/labels` | 社团列表页 | 社团卡片列表 |
| `/label/:id` | 社团详情页 | 社团信息、专辑列表、成员列表 |
| `/tag` | 分类页 | 按标签 + 价格（免费/付费）筛选 |
| `/user/:id` | 用户页 | 后期实现，Mock 阶段可搭壳 |
