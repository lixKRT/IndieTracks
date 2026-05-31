# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech Stack

- **Vue 3** (Options API + Composition API `<script setup>` 混用)
- **Vite 8** — `npm run dev` / `npm run build` / `npm run preview`
- **Vue Router 4** — `createWebHistory`，无 hash 模式
- **Pinia 3** — 全局状态管理，两个 store：`player` / `favorite`
- **Axios** — 已安装，尚未接入（当前用 `src/api/mock.js` 模拟数据）

## Architecture

```
src/
├── api/mock.js          # 模拟 API（fetchAlbums / fetchAlbum / fetchCircles / fetchCircle / getTags / fetchUser）
├── components/
│   ├── molecules/       # AlbumCard, CircleCard, CommentItem, TrackRow
│   └── organisms/       # AlbumGrid, CommentSection, FooterSection, HeroSection, Navbar, PlayerBar, TagFilter, TrackList
├── layouts/MainLayout.vue  # 全局壳：Navbar + router-view + PlayerBar + FooterSection + Auth Modals
├── views/               # Home, AlbumDetail, LabelDetail, Labels, TagBrowse
├── stores/
│   ├── player.js        # 播放器状态（playlist / current_index / is_playing / is_expanded）
│   └── favorite.js      # 收藏状态（favoriteAlbumIds: Set）
├── styles/
│   ├── tokens.css       # CSS 自定义属性（颜色/间距/字体/过渡）
│   ├── reset.css        # 全局重置
│   └── utilities.css    # 容器/加载/模态框等通用样式
├── router/index.js      # 路由定义
└── main.js              # 入口
```

**层级关系**：`main.js → App.vue → MainLayout.vue → (Navbar + <router-view/> + PlayerBar + FooterSection)`

## Conventions

- **数据字段命名**：全 snake_case（与后端/数据库一致），如 `album_id`、`circle_name`、`file_type`、`cover_url`
- **CSS 变量**：所有颜色/间距必须引用 `tokens.css` 中的自定义属性，禁止硬编码
- **组件层级**：molecules（原子）→ organisms（组合）→ layouts（布局）→ views（页面）
- **响应式断点**：`@media (max-width: 768px)` 为移动端临界点
- **图片占位**：当前使用 `placehold.co` 占位图，后续替换为 MinIO 对象存储

## Styling Theme

暗黑直角风格，参考 dizzylab.net：
- 背景 `#0a0a0a`，强调色 `#ff6b6b`，hover 态 `#ff8787`
- 边框 `#222` / `#333`，卡片背景 `#1a1a1a`
- 字体：Inter / PingFang SC / Microsoft YaHei
- 无圆角（border-radius: 0 或极小值）

## State Management

**Player Store** (`stores/player.js`)：
- Composition API (`defineStore` + `setup` 函数)
- localStorage key: `indietracks_player`，持久化 playlist + current_index
- 核心方法：`playAlbumTracks` / `addAlbumTracks` / `jumpToTrack` / `prev` / `next` / `reorder`
- 只播放 `file_type === 'preview'` 的曲目

**Favorite Store** (`stores/favorite.js`)：
- Options API (`defineStore` + 对象格式)
- localStorage key: `indie-tracks-favorites`，持久化为 JSON 数组
- 在 `main.js` 中调用 `initFromStorage()` 初始化

## Mock API (`api/mock.js`)

所有 API 函数均为 async（带随机延迟），返回格式与预期后端一致：

| 函数 | 参数 | 返回 |
|---|---|---|
| `fetchAlbums` | `{ page, page_size, tag, search, price, sort }` | `{ data, total, page, page_size }` |
| `fetchAlbum` | `album_id` | 专辑详情（含 tracks / comments / circle / tags） |
| `fetchCircles` | `{}` | `{ data }` — 增强版社团列表（含 preview_albums / representative_tags） |
| `fetchCircle` | `circle_id` | 社团详情（含 albums / members） |
| `getTags` | 无 | 标签数组（同步） |
| `fetchUser` | `user_id` | 用户详情 |

## Routes

| Path | View | 说明 |
|---|---|---|
| `/` | `Home.vue` | Hero + 最新专辑网格 + 热门社团横向滚动 |
| `/album/:id` | `AlbumDetail.vue` | 左右布局：封面+社团信息+曲目列表 / 购买卡片+评论 |
| `/labels` | `Labels.vue` | 社团卡片网格（含专辑堆叠预览） |
| `/label/:id` | `LabelDetail.vue` | 社团详情 Hero + 成员列表 + 专辑网格 |
| `/tag` | `TagBrowse.vue` | 标签筛选 + 专辑网格，支持 URL query 参数同步 |

## PlayerBar

固定在页面底部（`position: fixed; bottom: 0`），两种状态：
- **收起态**：当前曲目名 + 播放/暂停/上下曲 + 进度条
- **展开态**：额外显示播放列表（支持拖拽排序、移除、清空）
- `MainLayout.vue` 中 `.layout-main` 的 `padding-bottom: 80px` 为播放器预留空间

## Development Notes

- 当前所有页面数据来自 `mock.js`，切换真实 API 时只需替换 import 来源
- 组件样式全部 `<style scoped>`，全局样式仅在 `styles/` 目录下
- 没有 ESLint / Prettier 配置，代码风格靠约定维持
- 没有测试框架，`npm run build` 是唯一的代码验证手段
