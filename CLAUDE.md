# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IndieTracks is an indie music showcase and preview platform (reference: dizzylab.net). Three-tier architecture: Vue 3 frontend, Spring Boot backend, Scrapy crawler for dizzylab data.

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

### Crawler
```bash
cd crawler
.\env\Scripts\activate                              # Activate venv (Windows)
scrapy crawl album_test                             # Run test spider
python setup_db.py                                  # Initialize DB from SQL
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
├── crawler/               # Scrapy project
│   ├── indietracks_spider/
│   │   ├── spiders/album_test.py  # Main spider (album list → detail → buyers → comments → circle)
│   │   ├── pipelines.py           # PostgreSQL upsert pipeline with ID caching
│   │   ├── items.py               # 14 Scrapy Item classes (1:1 with DB tables)
│   │   ├── settings.py            # Dynamic config from JSON files
│   │   └── utils/
│   │       ├── config_loader.py   # Reads crawler/config/*.json
│   │       └── delay.py           # Between-albums sleep controller
│   ├── config/
│   │   ├── database.json          # DB credentials
│   │   └── delay.json             # Rate-limit strategies (default/gentle/test)
│   └── setup_db.py               # Execute SQL script
└── database/
    ├── create_database.sql        # Full schema (12 tables, indexes)
    └── init.sql                   # TRUNCATE + reset sequences
```

## Database Schema (12 tables)

- `users` — dizzylab_user_id UNIQUE, user_role: normal/pro/staff
- `circles` — dizzylab_labelid UNIQUE, music groups
- `user_circles` — user-circle membership (many-to-many)
- `albums` — dizzylab_id UNIQUE, info_title + info_content replace description
- `album_circles` — album-circle (many-to-many, equal)
- `work_files` — album tracks, file_type: preview/full
- `tags` / `album_tags` — tag classification (many-to-many)
- `comments` — user reviews on albums
- `favorites` — user-albook likes (many-to-many)
- `owned_albums` — purchase records
- `user_follows` / `circle_follows` — follow relationships

All tables use SERIAL PKs. Unique indexes on dizzylab_id/dizzylab_user_id/dizzylab_labelid.

## Key Conventions

- **snake_case** everywhere: DB columns = backend JSON keys = frontend mock data fields
- **Dark flat theme**: bg `#0a0a0a`, accent `#ff6b6b`, CSS custom properties in tokens.css
- **Component layers**: molecules → organisms → layouts → views (no atoms layer)
- **Player**: Pinia store with localStorage persistence, plays only preview tracks, Spotify-style bottom bar
- **Mock phase**: All frontend data comes from `api/mock.js`, no real backend calls yet
- **Crawler pipeline**: postgres upsert with in-memory ID caches (dizzylab_id → db_id); work_files use delete-then-insert per album
- **Crawler delay**: configurable strategies in delay.json, album_test spider runs single-threaded with between-album sleep

## Crawler Architecture

Spider `album_test` follows this flow per album:
1. Fetch album list from API → parse each album detail page
2. Yield items: Album → WorkFiles → Tags → AlbumTags → Circle → AlbumCircle
3. Sub-requests: buyers API → parse_buyers (User + OwnedAlbum), comments API → parse_comments (User + Comment), circle page → parse_circle_detail (User + UserCircle)

Pipeline resolves cross-references via `_dizzylab_id`, `_tag_name` etc. temporary fields on items, looked up through in-memory caches.

## Page Status

| Route | Phase |
|-------|-------|
| `/` Home | P2 Done |
| `/album/:id` Detail | P3 In Progress |
| `/labels` Circle list | P5 |
| `/label/:id` Circle detail | P5 |
| `/tag` Tag browse | P6 |
| `/user/:id` User page | Later |
