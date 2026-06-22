# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech Stack

- **Vue 3** (Composition API + Options API 混用)
- **Vite 8** — `npm run dev` / `npm run build` / `npm run preview`
- **Vue Router 4** — `createWebHistory`，无 hash 模式
- **Pinia 3** — 全局状态管理，三个 store：`user` / `player` / `favorite`
- **Axios** — HTTP 请求，baseURL: `/api`
- **Font Awesome 6** — 图标库（CDN 引入）

## Architecture

```
src/
├── api/
│   ├── request.js          # Axios 实例 + 40+ API 函数
│   └── index.js            # 统一导出
├── components/
│   ├── atoms/              # EmptyState, LoadingSpinner
│   ├── molecules/          # AlbumCard, CircleCard, CommentItem, PurchaseModal, TrackRow
│   └── organisms/          # AlbumGrid, CommentSection, FooterSection, HeroSection, Navbar, PlayerBar, TagFilter, TrackList
├── composables/            # authGuard, navigation, previewPlay
├── layouts/
│   └── MainLayout.vue      # 全局壳：Navbar + router-view + PlayerBar + FooterSection + Auth Modals
├── router/
│   └── index.js            # 路由配置（8 个路由）
├── stores/
│   ├── user.js             # 用户认证状态
│   ├── player.js           # 播放器状态
│   └── favorite.js         # 收藏状态
├── styles/
│   ├── tokens.css          # CSS 自定义属性（颜色/间距/字体/过渡）
│   ├── reset.css           # 全局重置
│   └── utilities.css       # 容器/加载/模态框等通用样式
├── utils/
│   └── text.js             # cleanText() 清理爬虫数据
└── views/                  # 8 个页面组件
```

**层级关系**：`main.js → App.vue → MainLayout.vue → (Navbar + <router-view/> + PlayerBar + FooterSection)`

## Conventions

- **数据字段命名**：全 snake_case（与后端/数据库一致），如 `album_id`、`circle_name`、`file_type`、`cover_url`
- **CSS 变量**：所有颜色/间距必须引用 `tokens.css` 中的自定义属性，禁止硬编码
- **组件层级**：atoms → molecules → organisms → layouts → views
- **响应式断点**：`@media (max-width: 768px)` 为移动端临界点
- **图标**：使用 Font Awesome 6（`fas fa-*`），CDN 引入

## Styling Theme

暗黑直角风格，参考 dizzylab.net：
- 背景 `#0a0a0a`，强调色 `#ff6b6b`，hover 态 `#ff8787`
- 边框 `#222` / `#333`，卡片背景 `#1a1a1a`
- 字体：Inter / PingFang SC / Microsoft YaHei
- 无圆角（border-radius: 0 或极小值）

### 按钮风格

- **播放按钮**：描边风格（`border: 1px solid accent`），hover 时填充
- **播放中指示器**：竖条动画（3 个竖条交替伸缩）
- **播放器控制**：描边圆形播放按钮，hover 时填充

## State Management

**User Store** (`stores/user.js`)：
- Composition API
- 状态：user, isLoggedIn
- 方法：doRegister, doLogin, doLogout, init (fetchMe)

**Player Store** (`stores/player.js`)：
- Composition API
- localStorage key: `indietracks_player`，持久化 playlist + current_index
- 核心方法：`playAlbumTracks` / `addAlbumTracks` / `jumpToTrack` / `prev` / `next` / `reorder`
- 只播放 `file_type === 'preview'` 的曲目

**Favorite Store** (`stores/favorite.js`)：
- Options API
- localStorage key: `indie-tracks-favorites`，持久化为 JSON 数组
- 在 `main.js` 中调用 `initFromStorage()` 初始化

## API Layer

`api/request.js` 导出 40+ 函数，覆盖：
- 专辑：fetchAlbums, fetchAlbum, fetchRecommendations
- 社团：fetchCircles, fetchCircle
- 标签：getTags
- 用户：fetchUser, getUserFavorites, getUserFollowingCircles, getUserFollowingUsers
- 评论：fetchComments, addComment, updateComment, deleteComment
- 收藏：getFavorites, addFavorite, removeFavorite, checkFavorite
- 购买：purchaseAlbum, checkPurchased, getUserPurchases
- 购物车：getCart, addToCart, removeFromCart, getCartCount, checkInCart, checkoutCart
- 关注：followCircle, unfollowCircle, checkCircleFollow, followUser, unfollowUser, checkUserFollow
- 认证：register, login, logout, fetchMe, uploadAvatar

## Routes

| Path | View | 说明 |
|---|---|---|
| `/` | `Home.vue` | Hero + 最新专辑网格 + 热门社团横向滚动 |
| `/album/:id` | `AlbumDetail.vue` | 左右布局：封面+社团信息+曲目列表 / 购买卡片+评论 |
| `/labels` | `Labels.vue` | 社团卡片网格（分页加载） |
| `/label/:id` | `LabelDetail.vue` | 社团详情 Hero + 成员列表 + 专辑网格 |
| `/tag` | `TagBrowse.vue` | 标签筛选 + 专辑网格，支持 URL query 参数同步 |
| `/user/:id` | `UserProfile.vue` | 用户页：收藏/已购买/关注 |
| `/cart` | `CartView.vue` | 购物车：商品列表 + 结算面板 |
| `/admin` | `Dashboard.vue` | 数据透视页（pro, staff） |
| `/admin/albums` | `AlbumList.vue` | 专辑管理列表（pro, staff） |
| `/admin/albums/create` | `AlbumForm.vue` | 新增专辑（pro, staff） |
| `/admin/albums/:id/edit` | `AlbumForm.vue` | 编辑专辑（pro, staff） |
| `/admin/circles` | `CircleList.vue` | 社团管理列表（staff） |
| `/admin/circles/:id` | `CircleDetail.vue` | 社团详情/成员管理（staff） |
| `/admin/users` | `UserList.vue` | 用户管理列表（staff） |
| `/admin/tags` | `TagList.vue` | 标签管理列表（pro, staff） |
| `/admin/comments` | `CommentList.vue` | 评论管理列表（pro, staff） |
| `/:pathMatch(.*)*` | `NotFound.vue` | 404 页面 |

## Components

**PurchaseModal** (`components/molecules/PurchaseModal.vue`)：
- 购买确认浮窗，使用 Teleport 渲染到 body
- Props: `album`（对象）, `visible`（布尔）, `purchasing`（布尔）
- Events: `close`, `confirm`
- 显示专辑封面、名称、社团、价格
- 确认按钮带 loading 动画

**PlayerBar** (`components/organisms/PlayerBar.vue`)：
- 固定在页面底部（`position: fixed; bottom: 0`）
- 收起态：当前曲目名 + 播放/暂停/上下曲 + 进度条
- 展开态：额外显示播放列表（支持拖拽排序、移除、清空）
- `MainLayout.vue` 中 `.layout-main` 的 `padding-bottom: 80px` 为播放器预留空间

**Navbar** (`components/organisms/Navbar.vue`)：
- 登录后显示购物车图标（头像左侧）+ 角标
- 购物车角标监听 `cart-updated` 事件自动刷新
- ≤768px 汉堡菜单

## Development Notes

- 组件样式全部 `<style scoped>`，全局样式仅在 `styles/` 目录下
- 没有 ESLint / Prettier 配置，代码风格靠约定维持
- 没有测试框架，`npm run build` 是唯一的代码验证手段
