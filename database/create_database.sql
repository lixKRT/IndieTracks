-- ============================================================
-- IndieTracks 数据库建表脚本
-- 用法：psql -U postgres -d indietracks -f create_database.sql
-- ============================================================

-- ── 用户表 ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id         SERIAL PRIMARY KEY,
    dizzylab_user_id INT UNIQUE,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(100) UNIQUE,
    password_hash   VARCHAR(255),
    avatar_url      VARCHAR(500),
    user_role       VARCHAR(10) DEFAULT 'normal'
                    CHECK (user_role IN ('normal', 'pro', 'staff')),
    created_at          TIMESTAMP DEFAULT NOW(),
    userpage_crawled_at TIMESTAMP
);

-- ── 社团表 ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS circles (
    circle_id         SERIAL PRIMARY KEY,
    dizzylab_labelid  INT UNIQUE,
    name              VARCHAR(100) NOT NULL,
    description       TEXT,
    logo_url          VARCHAR(500),
    owner_user_id     INT REFERENCES users(user_id) ON DELETE SET NULL
);

-- ── 用户-社团关联表 ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_circles (
    user_id    INT REFERENCES users(user_id) ON DELETE CASCADE,
    circle_id  INT REFERENCES circles(circle_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, circle_id)
);

-- ── 专辑表 ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS albums (
    album_id      SERIAL PRIMARY KEY,
    dizzylab_id   VARCHAR(50) UNIQUE NOT NULL,
    title         VARCHAR(200) NOT NULL,
    info_title    TEXT,
    info_content  TEXT,
    price         DECIMAL(10,2) DEFAULT 0,
    cover_url     VARCHAR(500),
    publish_date  TIMESTAMP DEFAULT NOW()
);

-- ── 专辑-社团关联表（多对多，完全平等）─────────────────
CREATE TABLE IF NOT EXISTS album_circles (
    album_id   INT REFERENCES albums(album_id) ON DELETE CASCADE,
    circle_id  INT REFERENCES circles(circle_id) ON DELETE CASCADE,
    PRIMARY KEY (album_id, circle_id)
);

-- ── 专辑文件表（音频）───────────────────────────────────
CREATE TABLE IF NOT EXISTS work_files (
    file_id       SERIAL PRIMARY KEY,
    album_id      INT REFERENCES albums(album_id) ON DELETE CASCADE,
    file_name     VARCHAR(200) NOT NULL,
    object_key    VARCHAR(500),
    file_type     VARCHAR(10) NOT NULL
                  CHECK (file_type IN ('preview', 'full')),
    track_length  VARCHAR(10),
    file_size     BIGINT DEFAULT 0,
    sort_order    INT DEFAULT 0
);

-- ── 标签表 ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tags (
    tag_id  SERIAL PRIMARY KEY,
    name    VARCHAR(50) UNIQUE NOT NULL
);

-- ── 专辑-标签关联表 ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS album_tags (
    album_id  INT REFERENCES albums(album_id) ON DELETE CASCADE,
    tag_id    INT REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (album_id, tag_id)
);

-- ── 评论表 ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comments (
    comment_id  SERIAL PRIMARY KEY,
    user_id     INT REFERENCES users(user_id) ON DELETE SET NULL,
    album_id    INT REFERENCES albums(album_id) ON DELETE CASCADE,
    content     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

SELECT current_database();

-- ── 收藏表 ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS favorites (
    user_id    INT REFERENCES users(user_id) ON DELETE CASCADE,
    album_id   INT REFERENCES albums(album_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, album_id)
);

-- ── 用户已拥有专辑表（购买记录） ──────────────────────
CREATE TABLE IF NOT EXISTS owned_albums (
    user_id    INT REFERENCES users(user_id) ON DELETE CASCADE,
    album_id   INT REFERENCES albums(album_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, album_id)
);

-- ── 用户关注用户表 ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_follows (
    user_id           INT REFERENCES users(user_id) ON DELETE CASCADE,
    followed_user_id  INT REFERENCES users(user_id) ON DELETE CASCADE,
    created_at        TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, followed_user_id)
);

-- ── 用户关注社团表 ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS circle_follows (
    user_id    INT REFERENCES users(user_id) ON DELETE CASCADE,
    circle_id  INT REFERENCES circles(circle_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, circle_id)
);

-- ════════════════════════════════════════════════════════
-- 索引
-- ════════════════════════════════════════════════════════

CREATE INDEX IF NOT EXISTS idx_work_files_album_id        ON work_files(album_id);
CREATE INDEX IF NOT EXISTS idx_work_files_file_type       ON work_files(file_type);
CREATE INDEX IF NOT EXISTS idx_comments_album_id          ON comments(album_id);
CREATE INDEX IF NOT EXISTS idx_favorites_user_id          ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_albums_publish_date        ON albums(publish_date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_albums_dizzylab_id   ON albums(dizzylab_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_dizzylab_user_id ON users(dizzylab_user_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_circles_dizzylab_labelid ON circles(dizzylab_labelid);
CREATE INDEX IF NOT EXISTS idx_user_follows_user_id       ON user_follows(user_id);
CREATE INDEX IF NOT EXISTS idx_user_follows_followed_user_id ON user_follows(followed_user_id);
CREATE INDEX IF NOT EXISTS idx_circle_follows_user_id     ON circle_follows(user_id);
CREATE INDEX IF NOT EXISTS idx_circle_follows_circle_id   ON circle_follows(circle_id);
CREATE INDEX IF NOT EXISTS idx_owned_albums_user_id       ON owned_albums(user_id);
CREATE INDEX IF NOT EXISTS idx_owned_albums_album_id      ON owned_albums(album_id);

-- ── 迁移：user_pages 爬虫追踪字段（安全幂等） ──────────
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'userpage_crawled_at'
    ) THEN
        ALTER TABLE users ADD COLUMN userpage_crawled_at TIMESTAMP;
    END IF;
END $$;
