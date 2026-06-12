# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

IndieTracks is an indie music showcase and preview platform (reference: dizzylab.net). Three-tier architecture: Vue 3 frontend, Spring Boot backend, Scrapy crawler for dizzylab data.

> **Crawler 相关 → `crawler/CLAUDE.md` | 脚本相关 → `scripts/CLAUDE.md` | 数据库设计 → `docs/数据库ER图与DDL.md`**

## Tech Stack

- **Frontend**: Vue 3 + Vite 8 + Vue Router 4 + Pinia + Axios + Font Awesome 6
- **Backend**: Spring Boot 4 + Java 25 + MyBatis-Plus + Jetty + Spring Security
- **Data**: PostgreSQL 18 + MinIO object storage (Nginx 代理访问)
- **Auth**: HttpOnly Cookie + JWT, BCrypt password encryption
- **Crawler**: Scrapy (Python 3.13) targeting dizzylab.net

## Commands

### Frontend
```bash
cd frontend
npm run dev       # Start Vite dev server
npm run build     # Production build
npm run preview   # Preview production build
```

### Backend
```bash
cd backend
./mvnw spring-boot:run          # Start backend
./mvnw test                      # Run tests
./mvnw clean compile             # Compile only
```

### Linux 部署
```bash
bash scripts/linux/setup-all.sh          # 一键部署
bash scripts/linux/deploy.sh             # 重新构建部署
bash scripts/linux/stop-all.sh           # 一键停止
systemctl start indietracks              # 启动所有服务（含依赖）
systemctl stop indietracks               # 停止所有服务
```

### Crawler & Database
```bash
# Linux
bash scripts/linux/setup-crawler.sh      # 爬虫一键部署
bash scripts/linux/run-crawlers.sh       # 爬虫启动器

# Windows
python scripts/windows/setup-crawler.py  # 爬虫一键部署
python scripts/windows/run-crawlers.py   # 爬虫启动器

# 通用
cd crawler && python -m pytest tests/ -v # 爬虫单元测试（195 个）
```

## Project Structure

```
IndieTracks/
├── frontend/              # Vue 3 SPA
├── backend/               # Spring Boot
├── crawler/               # Scrapy project → crawler/CLAUDE.md
├── scripts/               # 运维脚本 → scripts/CLAUDE.md
│   ├── linux/             # Linux 部署脚本
│   └── windows/           # Windows 爬虫脚本
├── database/
│   ├── create_database.sql  # 14 tables + migrations
│   └── init.sql             # TRUNCATE + reset
├── docs/                  # 项目文档
└── tools/minio/           # MinIO 二进制（gitignored）
```

## Key Conventions

- **snake_case** everywhere: DB columns = backend JSON keys = frontend fields
- **Dark flat theme**: bg `#0a0a0a`, accent `#ff6b6b`, CSS custom properties in tokens.css
- **Component layers**: atoms → molecules → organisms → layouts → views
- **Player**: Pinia store with localStorage persistence, Spotify-style bottom bar

## Page Status

| Route | Phase |
|-------|-------|
| `/` Home | ✅ 联调完成 |
| `/album/:id` Detail | ✅ 联调完成 |
| `/labels` Circle list | ✅ 联调完成 |
| `/label/:id` Circle detail | ✅ 联调完成 |
| `/tag` Tag browse | ✅ 联调完成 |
| `/user/:id` User page | ✅ 联调完成 |
| `/cart` Cart | ✅ 联调完成 |
