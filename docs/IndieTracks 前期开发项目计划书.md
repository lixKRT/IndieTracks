好的，根据你最新的要求，我重新撰写了一份**前期开发阶段**的项目计划书。这份计划书聚焦于团队当前需要做的事，结构更灵活，没有指定具体分工。

---

## IndieTracks 前期开发项目计划书

### 一、项目概述

**项目名称**：IndieTracks 独立音乐作品展示平台

**项目目标**：构建一个类似 Dizzylab 的独立音乐作品展示与试听平台，支持专辑浏览、在线试听、社团展示等功能。项目分为爬虫数据采集、后端 API 服务、前端页面展示三大模块。

**开发策略**：先集中完成前端所有页面（使用 Mock 数据），再开发后端 API，最后接入爬虫采集的真实数据。前后端通过约定的接口文档解耦，互不阻塞。

---

### 二、技术栈

| 层 | 技术 |
|:---|:---|
| 前端 | Vue 3 + Vite 8 + Vue Router 4 + Axios + Pinia |
| 后端 | Spring Boot 4 + Java 25 + Spring Data JPA + Undertow |
| 数据库 | PostgreSQL 18 |
| 对象存储 | MinIO（存放音频文件和封面图） |
| 爬虫 | Scrapy + psycopg2 + minio Python SDK |
| 部署 | Ubuntu Server 22.04 + Nginx（开发阶段暂不需要） |

**版本说明**：
- PostgreSQL 使用 **18** 版本。
- Scrapy、Python 不强制指定版本，使用当前稳定版即可。
- 其他依赖版本由包管理器自动管理。

---

### 三、项目结构（大体框架）

```
indietracks/
├── frontend/                  # Vue 3 前端（四人共同开发）
│   ├── src/
│   │   ├── views/             # 页面
│   │   ├── components/        # 组件
│   │   ├── api/               # Axios 封装 + Mock 数据
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态
│   │   └── styles/            # 全局样式与拟态变量
│   └── package.json
│
├── backend/                   # Spring Boot 后端（前期暂不重点开发）
│   ├── src/main/java/
│   └── pom.xml
│
├── crawler/                   # Scrapy 爬虫（一人负责）
│   ├── indietracks_spider/
│   └── scrapy.cfg
│
├── database/
│   ├── init.sql               # 建表脚本
│   └── seed.sql               # 种子数据（爬虫产出后导出）
│
├── tools/                     # MinIO 等二进制文件
├── scripts/                   # 启动脚本
├── data/                      # 运行时数据（不提交 Git）
└── docs/                      # 文档
```

---

### 四、开发阶段划分（AI给的，后面我们商量一下）

#### 阶段一：前端全页面开发（当前阶段）

**目标**：完成所有页面的 UI 与交互，使用 Mock 数据驱动，无需后端和数据库。

| 事项 | 说明 |
|:---|:---|
| **页面清单** | 首页、专辑详情页、社团页、作品列表页 |
| **公共组件** | 专辑卡片（AlbumCard）、导航栏（AppHeader）、页脚（AppFooter）、播放器组件（AudioPlayer）等 |
| **Mock 数据** | 在 `api/mock.js` 中定义与后端约定好的模拟数据，字段名与将来后端完全一致 |
| **样式** | 统一使用拟态风格（Neumorphism），CSS 变量集中在 `variables.css` |
| **状态管理** | Pinia 管理播放器状态、作品列表缓存等全局数据 |
| **路由** | Vue Router 4 配置所有页面路由 |

**交付标准**：所有页面在 `npm run dev` 下可完整浏览，交互正常，Mock 数据能驱动页面渲染，视觉效果与预期一致。

#### 阶段二：后端 API 开发

**目标**：实现真实数据接口，替换前端 Mock。

| 事项 | 说明 |
|:---|:---|
| **核心接口** | `GET /api/works`（作品列表）、`GET /api/works/{id}`（作品详情）、`GET /api/files/{id}/presigned-url`（试听链接） |
| **数据库** | 使用 `database/init.sql` 建表，与 JPA 实体对应 |
| **MinIO 集成** | 生成预签名 URL，供前端直接播放音频 |

**交付标准**：Postman 测试三个接口返回正确 JSON，前端切换到真实接口后页面功能不变。

#### 阶段三：爬虫开发与数据导入

**目标**：采集真实数据，填充数据库和 MinIO。

| 事项 | 说明 |
|:---|:---|
| **爬取内容** | 专辑信息、曲目列表、试听音频片段、封面图、社团信息、评论 |
| **数据存储** | 写入 PostgreSQL 18，文件上传至 MinIO |
| **合规** | 严格遵循目标站 robots.txt，延时 ≥ 2 秒，并发 ≤ 4 |

**交付标准**：爬虫可独立运行，数据库中有至少 10 页、200 条以上作品数据，MinIO 中有对应音频文件。

#### 阶段四：联调、部署、文档

**目标**：全栈联调通过，服务器部署稳定，文档撰写完成。

| 事项 | 说明 |
|:---|:---|
| **联调** | 前端切换真实接口，全流程测试 |
| **部署** | 2G2C 服务器上启动后端、MinIO、Nginx，前端构建后由 Nginx 托管 |
| **文档** | 撰写项目文档（PDF），包含架构图、截图、接口说明 |

---

### 五、前端 Mock 数据规范

为保证前期开发顺利，Mock 数据与后端接口的对应关系已提前约定：

**作品列表（首页/列表页）**：
```javascript
{
  data: [
    {
      album_id: 1,
      title: "二次元律动 VOL.3",
      artist: "炒饭",
      cover_url: "https://...",
      category: "ACG"
    }
  ],
  total: 100,
  page: 1,
  page_size: 12
}
```

**作品详情（专辑详情页）**：
```javascript
{
  album_id: 1,
  title: "二次元律动 VOL.3",
  artist: "炒饭",
  cover_url: "https://...",
  description: "专辑介绍文字...",
  publish_date: "2026-05-01",
  circles: [{ name: "炒饭社团", logo_url: "..." }],
  tracks: [
    { file_id: 1, file_name: "God Knows...", duration: "4:25", sort_order: 1 }
  ],
  tags: ["ACG", "同人"],
  comments: [
    { username: "听众A", content: "很棒！", created_at: "2026-05-10" }
  ]
}
```

> **重要**：前端开发时，Mock 数据的字段名（如 `cover_url`、`file_id`）必须与后端数据库字段保持统一风格。建议全部使用**下划线命名**（snake_case），因为 PostgreSQL 默认不区分大小写，Spring Boot 也可以配置为返回原始列名。

---

### 六、团队协作约定

| 约定项 | 内容 |
|:---|:---|
| **分支策略** | `main`（稳定）→ `develop`（开发主线）→ 每人从 `develop` 拉功能分支 |
| **提交规范** | 使用约定式提交：`feat:` 新功能、`fix:` 修复、`style:` 样式、`docs:` 文档 |
| **代码风格** | 前端统一配置 ESLint + Prettier；后端遵循 IDEA 默认格式化 |
| **公共文件** | `variables.css`、`request.js`、路由配置等由一人统一维护，其他人通过 PR 修改 |
| **组件复用** | `AlbumCard.vue` 等公共组件放在 `components/common/`，所有页面统一引用 |

---

### 七、沟通与进度

- **日常沟通**：群内同步每日进度，遇到阻塞随时讨论。
- **代码审查**：合并到 `develop` 前至少一人 Review。
- **文档同步**：接口文档和 Mock 数据字段表更新后及时通知全员。

---

这份计划书已聚焦于当前最迫切的“前端先行”策略，分工由你们后续自行协商。接下来你们可以先集中精力把前端页面跑通，爬虫部分按你个人的节奏推进即可。