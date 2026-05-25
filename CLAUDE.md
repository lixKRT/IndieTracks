# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

IndieTracks is an indie music showcase and preview platform (reference: dizzylab.net). Three-tier architecture: Vue 3 frontend, Spring Boot backend, Scrapy crawler for dizzylab data.

> **Crawler 相关请查看 `crawler/CLAUDE.md`。**

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

### Database
```bash
psql -U postgres -d indietracks -f database/create_database.sql  # Create tables
psql -U postgres -d indietracks -f database/init.sql             # Clear all data, reset sequences
```

## Project Structure

```
IndieTracks/
├── frontend/              # Vue 3 SPA
│   └── src/
│       ├── api/mock.js    # Central mock data layer (all APIs return Promise with delay)
│       ├── components/    # Atomic design: molecules/ → organisms/
│       │   ├── molecules/ # AlbumCard, TrackRow, CommentItem, CircleCard
│       │   └── organisms/ # AlbumGrid, TrackList, PlayerBar, Navbar, TagFilter, etc.
│       ├── layouts/       # MainLayout (Navbar + router-view + PlayerBar + Footer)
│       ├── views/         # Home, AlbumDetail, Labels, LabelDetail, TagBrowse
│       ├── router/        # Vue Router config (6 routes)
│       ├── stores/        # Pinia store: player.js only (no auth store yet)
│       └── styles/        # tokens.css (vars), reset.css, utilities.css
├── backend/               # Spring Boot (scaffolded, minimal code)
│   └── src/main/java/com/indietracks/backend/
│       └── BackendApplication.java  # Entry point only
├── crawler/               # Scrapy project → see crawler/CLAUDE.md
└── database/
    ├── create_database.sql        # Full schema (14 tables, indexes)
    └── init.sql                   # TRUNCATE + reset sequences
```

## Key Conventions

- **snake_case** everywhere: DB columns = backend JSON keys = frontend mock data fields
- **Dark flat theme**: bg `#0a0a0a`, accent `#ff6b6b`, CSS custom properties in tokens.css
- **Component layers**: molecules → organisms → layouts → views (no atoms layer)
- **Player**: Pinia store with localStorage persistence, plays only preview tracks, Spotify-style bottom bar
- **Mock phase**: All frontend data comes from `api/mock.js`, no real backend calls yet

## Page Status

| Route | Phase |
|-------|-------|
| `/` Home | P2 Done |
| `/album/:id` Detail | P3 In Progress |
| `/labels` Circle list | P5 |
| `/label/:id` Circle detail | P5 |
| `/tag` Tag browse | P6 |
| `/user/:id` User page | Later |
