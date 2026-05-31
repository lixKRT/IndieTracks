# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Tech Stack

- **Spring Boot 4.0.6** + Java 25
- **MyBatis-Plus** (NOT JPA) — Mapper 接口 + XML SQL
- **PostgreSQL 18** — 数据库不可更改
- **MinIO** — 预签名 URL 生成
- **Undertow** — 替换 Tomcat
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
    │           └── MinIO SDK（预签名 URL）
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
├── controller/     # 接口层
├── service/        # 业务层
├── mapper/         # 持久层（MyBatis-Plus Mapper）
├── entity/         # 数据库实体（字段 snake_case，和表一一对应）
├── dto/            # API 返回对象（JOIN 查询结果）
├── config/         # JacksonConfig / MinioConfig / MyBatisPlusConfig / CorsConfig
└── BackendApplication.java
```

## Key Conventions

- **字段命名**：Entity 字段直接用 snake_case（`album_id`，非 `albumId`），和数据库列名一致
- **JSON 输出**：Jackson 原样输出 snake_case，无需 PropertyNamingStrategy 配置
- **DTO 分离**：Entity 和 API 返回用不同的类，JOIN 结果映射到 DTO
- **分页**：MyBatis-Plus `IPage<T>` 分页插件，返回格式 `{ data, total, page, page_size }`
- **预签名 URL**：MinIO 生成，默认有效期 7 天，填入 `AlbumDetail.tracks[].preview_url`

## Database

14 张表，schema 在 `database/create_database.sql`。**不可更改表结构。**

核心表：albums / circles / users / tags / work_files / comments
关联表：album_circles / album_tags / user_circles / favorites / owned_albums / circle_follows / user_follows

## API Endpoints

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/albums` | 专辑列表（分页+筛选） |
| GET | `/api/albums/{id}` | 专辑详情 |
| GET | `/api/circles` | 社团列表 |
| GET | `/api/circles/{id}` | 社团详情 |
| GET | `/api/tags` | 标签列表 |
| GET | `/api/users/{id}` | 用户详情 |

详细接口文档见 `docs/后端开发计划书.md`。

## Configuration

- `application.properties`：数据库连接、MinIO 连接、MyBatis-Plus 配置
- 敏感信息（密码、密钥）使用环境变量，不硬编码
- CORS 开发阶段允许 `localhost:5173`，部署时 Nginx 同域解决
