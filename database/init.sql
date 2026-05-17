-- ============================================================
-- IndieTracks 数据库初始化脚本（清空所有数据，重置序列）
-- 用法：psql -U postgres -d indietracks -f init.sql
-- ============================================================

-- 禁用外键检查以加快清空速度
SET session_replication_role = 'replica';

-- 清空所有表
TRUNCATE TABLE
    owned_albums,
    circle_follows,
    user_follows,
    favorites,
    comments,
    album_tags,
    album_circles,
    work_files,
    tags,
    user_circles,
    albums,
    circles,
    users
CASCADE;

-- 恢复外键检查
SET session_replication_role = 'origin';

-- 重置所有 SERIAL 序列
ALTER SEQUENCE users_user_id_seq          RESTART WITH 1;
ALTER SEQUENCE circles_circle_id_seq      RESTART WITH 1;
ALTER SEQUENCE albums_album_id_seq        RESTART WITH 1;
ALTER SEQUENCE work_files_file_id_seq     RESTART WITH 1;
ALTER SEQUENCE tags_tag_id_seq            RESTART WITH 1;
ALTER SEQUENCE comments_comment_id_seq    RESTART WITH 1;
