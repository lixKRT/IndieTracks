# ADR-0001: 生产环境使用 Nginx 作为反向代理

- **状态**: 已接受
- **日期**: 2026-06-01
- **决策者**: lixKRT

## 背景

项目有三种部署方式可选：

1. **Vite proxy**（开发阶段现状）— Vite dev server 的内置代理，仅适用于开发环境
2. **Nginx 反向代理** — Nginx serve 前端静态文件 + proxy API 到后端
3. **Spring Boot 内嵌静态资源** — 把前端 `dist/` 放进后端 `resources/static/`，一个 jar 搞定

开发阶段使用 Vite proxy，零配置且支持 HMR（热更新）。但 Vite dev server 不适合生产环境：性能差、无缓存、无 gzip、不支持 HTTPS。

## 决策

**生产环境使用 Nginx 替代 Vite proxy**，开发环境保持 Vite 不变。

具体架构：

```
浏览器 → Nginx (:80)
           ├── /         → /opt/indietracks/frontend/dist/  (静态文件)
           └── /api/*    → proxy_pass http://127.0.0.1:8080  (Spring Boot)
```

- 前端通过 `npm run build` 生成静态文件，Nginx 直接 serve
- API 请求由 Nginx 反向代理到同机的 Spring Boot 后端（端口 8080）
- Vue Router 使用 history 模式，Nginx 配置 `try_files $uri $uri/ /index.html` 处理 SPA 路由
- 前端和后端部署在同一台服务器

## 理由

选择 Nginx 而非 Spring Boot 内嵌静态资源的原因：

| 维度 | Nginx | Spring Boot 内嵌 |
|------|-------|-----------------|
| 静态文件性能 | 优秀（零拷贝、sendfile） | 一般（Java IO） |
| 缓存控制 | `expires` + `Cache-Control` | 需手动配置 |
| gzip 压缩 | 原生支持 | 需额外配置 |
| HTTPS | certbot 一键配置 | 需 Java SSL 配置 |
| 前后端独立更新 | 更新 dist/ 或 jar 互不影响 | 每次更新需重新打包 |
| 额外依赖 | 需安装 Nginx | 无 |

Nginx 在静态文件服务方面有明确的性能和运维优势，且是行业标准做法。

## 后果

### 正面
- 前端和后端可独立部署、独立更新
- 静态文件有缓存和 gzip，加载更快
- 未来加 HTTPS 只需 certbot，不改后端代码
- 服务器端口 80 对外，无需记忆端口号

### 负面
- 服务器需额外安装 Nginx
- 部署流程多一步（配置 Nginx）
- 需维护 `nginx.conf` 配置文件

### 风险
- Nginx 配置错误会导致 502（后端未启动时）或 404（try_files 未配置时）
- 缓解：`nginx -t` 验证配置，`scripts/linux/nginx.conf` 已提供正确模板

## 相关文件

- `scripts/linux/nginx.conf` — Nginx 配置模板
- `scripts/linux/deploy.sh` — 部署脚本
- `scripts/linux/indietracks.service` — Systemd 服务配置
