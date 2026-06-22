# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Tech Stack

- **Spring Boot 4.0.6** + Java 25
- **MyBatis-Plus** (NOT JPA) — Mapper 接口 + XML SQL
- **PostgreSQL 18** — 数据库不可更改
- **MinIO** — 对象存储，Nginx 代理访问
- **Jetty** — 嵌入式 Web 容器（替换 Tomcat）
- **Lombok** — `@Data` / `@Builder` / `@NoArgsConstructor` / `@AllArgsConstructor`

## Commands

```bash
cd backend
./mvnw spring-boot:run          # 启动后端（localhost:8080）
./mvnw test                     # 运行测试
./mvnw clean compile            # 编译
```

## Architecture

```
Controller → Service → Mapper → PostgreSQL
    │           │
    │           └── MinIO SDK（URL 构造）
    │
    └── DTO（JOIN 查询结果）
```

**三层架构**（课程设计要求）：
1. **Controller**：接收请求，调用 Service，返回 JSON
2. **Service**：业务逻辑，组装 DTO
3. **Mapper**：MyBatis-Plus 接口 + XML（复杂 JOIN 写 XML）

## Package Structure

```
com.indietracks.backend/
├── controller/          # 接口层（11 个）
│   ├── AlbumController
│   ├── AuthController
│   ├── CartController
│   ├── CircleController
│   ├── CircleFollowController
│   ├── CommentController
│   ├── FavoriteController
│   ├── OwnedAlbumController
│   ├── TagController
│   ├── UserController
│   └── UserFollowController
├── service/             # 业务层（12 个）
│   ├── AlbumService
│   ├── AuthService
│   ├── CartService
│   ├── CircleService
│   ├── CircleFollowService
│   ├── CommentService
│   ├── FavoriteService
│   ├── MinioService
│   ├── OwnedAlbumService
│   ├── TagService
│   ├── UserFollowService
│   └── UserService
├── mapper/              # 持久层（10 个接口 + 9 个 XML）
├── entity/              # 数据库实体（10 个，snake_case 字段）
├── dto/                 # API 返回对象（8 个）
├── config/              # 配置类（5 个）
├── filter/              # JWT 认证过滤器
├── handler/             # 全局异常处理器
├── resolver/            # @CurrentUser 参数解析器
├── annotation/          # 自定义注解
└── util/                # 工具类（JWT、URL 预签名）
```

## Key Conventions

- **字段命名**：Entity 字段直接用 snake_case（`album_id`，非 `albumId`），和数据库列名一致
- **JSON 输出**：Jackson 原样输出 snake_case，无需 PropertyNamingStrategy 配置
- **DTO 分离**：Entity 和 API 返回用不同的类，JOIN 结果映射到 DTO
- **分页**：MyBatis-Plus `IPage<T>` 分页插件，返回格式 `{ data, total, page, page_size }`
- **URL 构造**：MinIO 资源通过 `minio.url-prefix` 配置，dev 用完整 URL，prod 用 `/minio` 相对路径

## Database

14 张表，schema 在 `database/create_database.sql`。**不可更改表结构。**

核心表：users / circles / albums / tags / work_files / comments
关联表：album_circles / album_tags / user_circles / favorites / owned_albums / cart_items / circle_follows / user_follows

## API Endpoints

### 专辑
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/albums` | 专辑列表（分页+筛选） |
| GET | `/api/albums/{id}` | 专辑详情 |
| GET | `/api/albums/{id}/recommendations` | 随机推荐 5 张专辑 |
| GET | `/api/albums/{id}/comments` | 评论列表（分页） |
| POST | `/api/albums/{id}/comments` | 发表评论（需登录） |

### 社团
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/circles` | 社团列表（分页） |
| GET | `/api/circles/{id}` | 社团详情 |

### 标签 & 用户
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/tags` | 标签列表 |
| GET | `/api/users/{id}` | 用户详情 |
| GET | `/api/users/{id}/favorites` | 用户收藏列表 |
| GET | `/api/users/{id}/following-circles` | 用户关注社团列表 |
| GET | `/api/users/{id}/following-users` | 用户关注用户列表 |

### 认证
| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录 |
| POST | `/api/auth/logout` | 登出 |
| GET | `/api/auth/me` | 获取当前用户 |
| POST | `/api/auth/avatar` | 上传头像 |

### 收藏 & 购买 & 购物车
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/favorites` | 收藏列表 |
| POST | `/api/favorites/{albumId}` | 添加收藏 |
| DELETE | `/api/favorites/{albumId}` | 取消收藏 |
| GET | `/api/favorites/{albumId}/status` | 检查收藏状态 |
| GET | `/api/purchases` | 已购专辑列表 |
| POST | `/api/purchases/{albumId}` | 购买专辑 |
| GET | `/api/purchases/{albumId}/status` | 检查是否已购 |
| GET | `/api/cart` | 购物车列表 |
| POST | `/api/cart/{albumId}` | 加入购物车 |
| DELETE | `/api/cart/{albumId}` | 移除购物车 |
| GET | `/api/cart/count` | 购物车数量 |
| GET | `/api/cart/{albumId}/status` | 检查是否在购物车 |
| POST | `/api/cart/checkout` | 批量结算 |

### 关注
| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/circle-follows/{circleId}` | 关注社团 |
| DELETE | `/api/circle-follows/{circleId}` | 取消关注社团 |
| GET | `/api/circle-follows/{circleId}/status` | 检查关注状态 |
| POST | `/api/user-follows/{userId}` | 关注用户 |
| DELETE | `/api/user-follows/{userId}` | 取消关注用户 |
| GET | `/api/user-follows/{userId}/status` | 检查关注状态 |

### 评论
| 方法 | 路径 | 说明 |
|---|---|---|
| PUT | `/api/comments/{id}` | 编辑评论 |
| DELETE | `/api/comments/{id}` | 删除评论 |

### 管理接口（/api/admin/*）

#### Dashboard
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/admin/dashboard/stats` | 统计数据 |
| GET | `/api/admin/dashboard/trends` | 趋势数据 |
| GET | `/api/admin/dashboard/top-albums` | 热门专辑排行 |
| GET | `/api/admin/dashboard/top-circles` | 活跃社团排行 |
| GET | `/api/admin/dashboard/tag-distribution` | 标签分布 |

#### 专辑管理
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/admin/albums` | 专辑列表（分页+筛选） |
| POST | `/api/admin/albums` | 新增专辑 |
| PUT | `/api/admin/albums/{id}` | 编辑专辑 |
| DELETE | `/api/admin/albums/{id}` | 删除专辑 |
| POST | `/api/admin/albums/{id}/tags` | 添加专辑标签 |
| DELETE | `/api/admin/albums/{id}/tags/{tagId}` | 移除专辑标签 |
| DELETE | `/api/admin/albums/{id}/tracks/{trackId}` | 删除曲目 |

#### 文件上传
| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/admin/upload/cover` | 上传封面 |
| POST | `/api/admin/upload/avatar` | 上传头像 |
| POST | `/api/admin/upload/logo` | 上传社团 Logo |
| POST | `/api/admin/upload/audio` | 上传音频 |

#### 社团管理（Staff）
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/admin/circles` | 社团列表 |
| POST | `/api/admin/circles` | 新增社团 |
| PUT | `/api/admin/circles/{id}` | 编辑社团 |
| DELETE | `/api/admin/circles/{id}` | 删除社团 |
| GET | `/api/admin/circles/{id}/members` | 社团成员列表 |
| POST | `/api/admin/circles/{id}/members` | 添加成员 |
| DELETE | `/api/admin/circles/{id}/members/{userId}` | 移除成员 |

#### 用户管理（Staff）
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/admin/users` | 用户列表 |
| PUT | `/api/admin/users/{id}` | 编辑用户 |
| DELETE | `/api/admin/users/{id}` | 删除用户 |

#### 标签管理
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/admin/tags` | 标签列表 |
| POST | `/api/admin/tags` | 新增标签 |
| PUT | `/api/admin/tags/{id}` | 编辑标签 |
| DELETE | `/api/admin/tags/{id}` | 删除标签 |

#### 评论管理
| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/admin/comments` | 评论列表 |
| DELETE | `/api/admin/comments/{id}` | 删除评论 |

## Configuration

- `application.properties`：开发配置（数据库、MinIO、JWT）
- `application-prod.properties`：生产配置（环境变量占位符）
- 敏感信息（密码、密钥）使用环境变量，不硬编码
- CORS 开发阶段允许 `localhost:*`，部署时 Nginx 同域解决
