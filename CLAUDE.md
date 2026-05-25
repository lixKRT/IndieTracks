# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

IndieTracks is an indie music showcase and preview platform (reference: dizzylab.net). Three-tier architecture: Vue 3 frontend, Spring Boot backend, Scrapy crawler for dizzylab data.

> **Crawler 相关 → `crawler/CLAUDE.md` | 脚本相关 → `scripts/CLAUDE.md` | 数据库设计 → `docs/数据库ER图与DDL.md`**

## Tech Stack

- **Frontend**: Vue 3 + Vite 8 + Vue Router 4 + Pinia + Axios
- **Backend**: Spring Boot 4 + Java 25 + JPA + Undertow (replaces Tomcat)
- **Data**: PostgreSQL 18 + MinIO object storage
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

### Crawler & Database
```bash
python scripts/windows/run-crawlers.py       # 爬虫启动器（一键）
python scripts/windows/setup-database.py     # 建库建表
python scripts/windows/setup-minio.py        # MinIO 部署
```

## Project Structure

```
IndieTracks/
├── frontend/              # Vue 3 SPA
├── backend/               # Spring Boot (scaffolded)
├── crawler/               # Scrapy project → crawler/CLAUDE.md
├── scripts/               # 运维脚本 → scripts/CLAUDE.md
│   └── windows/
│       ├── _common.py
│       ├── setup-database.py
│       ├── setup-minio.py
│       └── run-crawlers.py
└── database/
    ├── create_database.sql        # 14 tables + migrations
    └── init.sql                   # TRUNCATE + reset
```

## Key Conventions

- **snake_case** everywhere: DB columns = backend JSON keys = frontend mock data fields
- **Dark flat theme**: bg `#0a0a0a`, accent `#ff6b6b`, CSS custom properties in tokens.css
- **Component layers**: molecules → organisms → layouts → views
- **Player**: Pinia store with localStorage persistence, Spotify-style bottom bar

## Page Status

| Route | Phase |
|-------|-------|
| `/` Home | P2 Done |
| `/album/:id` Detail | P3 In Progress |
| `/labels` Circle list | P5 |
| `/label/:id` Circle detail | P5 |
| `/tag` Tag browse | P6 |
| `/user/:id` User page | Later |
