package com.indietracks.backend.service.admin;

import com.indietracks.backend.mapper.*;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class AdminDashboardService {

    private final UserMapper userMapper;
    private final AlbumMapper albumMapper;
    private final CircleMapper circleMapper;
    private final CommentMapper commentMapper;
    private final FavoriteMapper favoriteMapper;
    private final TagMapper tagMapper;
    private final JdbcTemplate jdbcTemplate;

    public AdminDashboardService(UserMapper userMapper, AlbumMapper albumMapper,
                                  CircleMapper circleMapper, CommentMapper commentMapper,
                                  FavoriteMapper favoriteMapper, TagMapper tagMapper,
                                  JdbcTemplate jdbcTemplate) {
        this.userMapper = userMapper;
        this.albumMapper = albumMapper;
        this.circleMapper = circleMapper;
        this.commentMapper = commentMapper;
        this.favoriteMapper = favoriteMapper;
        this.tagMapper = tagMapper;
        this.jdbcTemplate = jdbcTemplate;
    }

    // ===== Staff 统计 =====

    public Map<String, Object> getStaffStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalUsers", userMapper.selectCount(null));
        // 只统计有内容的专辑
        Integer albumCount = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM albums WHERE info_title IS NOT NULL OR info_content IS NOT NULL", Integer.class);
        stats.put("totalAlbums", albumCount != null ? albumCount : 0);
        stats.put("totalCircles", circleMapper.selectCircleCount());
        stats.put("totalComments", commentMapper.selectCount(null));
        stats.put("totalFavorites", favoriteMapper.selectCount(null));
        return stats;
    }

    public Map<String, Object> getStaffTrends(String period) {
        Map<String, Object> trends = new HashMap<>();
        String dateFilter = getDateFilter(period);

        List<Map<String, Object>> userTrends = jdbcTemplate.queryForList(
            "SELECT TO_CHAR(created_at, 'YYYY-MM') AS month, COUNT(*) AS count " +
            "FROM users WHERE created_at >= " + dateFilter +
            " GROUP BY month ORDER BY month");
        trends.put("userTrends", userTrends);

        List<Map<String, Object>> albumTrends = jdbcTemplate.queryForList(
            "SELECT TO_CHAR(publish_date, 'YYYY-MM') AS month, COUNT(*) AS count " +
            "FROM albums WHERE publish_date >= " + dateFilter +
            " AND (info_title IS NOT NULL OR info_content IS NOT NULL)" +
            " GROUP BY month ORDER BY month");
        trends.put("albumTrends", albumTrends);

        return trends;
    }

    public List<Map<String, Object>> getStaffTopAlbums(String period, int limit) {
        String dateFilter = getDateFilter(period);
        List<Map<String, Object>> albums = jdbcTemplate.queryForList(
            "SELECT a.album_id, a.title, a.cover_url, c.name AS circle_name, " +
            "COALESCE(f.fav_count, 0) AS favorite_count " +
            "FROM albums a " +
            "LEFT JOIN album_circles ac ON a.album_id = ac.album_id " +
            "LEFT JOIN circles c ON ac.circle_id = c.circle_id " +
            "LEFT JOIN (SELECT album_id, COUNT(*) AS fav_count FROM favorites GROUP BY album_id) f ON a.album_id = f.album_id " +
            "WHERE (a.info_title IS NOT NULL OR a.info_content IS NOT NULL) " +
            "AND a.publish_date >= " + dateFilter + " " +
            "ORDER BY favorite_count DESC LIMIT " + limit);
        for (Map<String, Object> album : albums) {
            applyUrlPrefix(album, "cover_url");
        }
        return albums;
    }

    public List<Map<String, Object>> getStaffTopCircles(String period, int limit) {
        String dateFilter = getDateFilter(period);
        List<Map<String, Object>> circles = jdbcTemplate.queryForList(
            "SELECT c.circle_id, c.name, c.logo_url, c.member_count, " +
            "COALESCE(ac.album_count, 0) AS album_count " +
            "FROM circles c " +
            "LEFT JOIN (SELECT circle_id, COUNT(*) AS album_count FROM album_circles ac2 " +
            "JOIN albums a ON ac2.album_id = a.album_id WHERE a.publish_date >= " + dateFilter +
            " GROUP BY circle_id) ac ON c.circle_id = ac.circle_id " +
            "ORDER BY album_count DESC LIMIT " + limit);
        for (Map<String, Object> circle : circles) {
            applyUrlPrefix(circle, "logo_url");
        }
        return circles;
    }

    public List<Map<String, Object>> getStaffTagDistribution() {
        return jdbcTemplate.queryForList(
            "SELECT t.tag_id, t.name, COUNT(at2.album_id) AS album_count " +
            "FROM tags t " +
            "LEFT JOIN album_tags at2 ON t.tag_id = at2.tag_id " +
            "GROUP BY t.tag_id, t.name " +
            "ORDER BY album_count DESC LIMIT 30");
    }

    // ===== Pro 统计（仅所属社团） =====

    public Map<String, Object> getProStats(Integer userId) {
        Map<String, Object> stats = new HashMap<>();
        List<Integer> circleIds = circleMapper.selectCircleIdsByUserId(userId);

        if (circleIds.isEmpty()) {
            stats.put("totalAlbums", 0);
            stats.put("totalComments", 0);
            stats.put("totalFavorites", 0);
            return stats;
        }

        String circleIdStr = circleIds.toString().replace("[", "").replace("]", "");

        Integer albumCount = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM album_circles WHERE circle_id IN (" + circleIdStr + ")", Integer.class);
        stats.put("totalAlbums", albumCount != null ? albumCount : 0);

        Integer commentCount = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM comments cm JOIN album_circles ac ON cm.album_id = ac.album_id WHERE ac.circle_id IN (" + circleIdStr + ")", Integer.class);
        stats.put("totalComments", commentCount != null ? commentCount : 0);

        Integer favCount = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM favorites f JOIN album_circles ac ON f.album_id = ac.album_id WHERE ac.circle_id IN (" + circleIdStr + ")", Integer.class);
        stats.put("totalFavorites", favCount != null ? favCount : 0);

        return stats;
    }

    public Map<String, Object> getProTrends(Integer userId, String period) {
        Map<String, Object> trends = new HashMap<>();
        List<Integer> circleIds = circleMapper.selectCircleIdsByUserId(userId);
        if (circleIds.isEmpty()) {
            trends.put("albumTrends", Collections.emptyList());
            return trends;
        }
        String circleIdStr = circleIds.toString().replace("[", "").replace("]", "");
        String dateFilter = getDateFilter(period);

        List<Map<String, Object>> albumTrends = jdbcTemplate.queryForList(
            "SELECT TO_CHAR(a.publish_date, 'YYYY-MM') AS month, COUNT(*) AS count " +
            "FROM albums a JOIN album_circles ac ON a.album_id = ac.album_id " +
            "WHERE ac.circle_id IN (" + circleIdStr + ") AND a.publish_date >= " + dateFilter +
            " GROUP BY month ORDER BY month");
        trends.put("albumTrends", albumTrends);
        return trends;
    }

    public List<Map<String, Object>> getProTopAlbums(Integer userId, String period, int limit) {
        List<Integer> circleIds = circleMapper.selectCircleIdsByUserId(userId);
        if (circleIds.isEmpty()) return Collections.emptyList();
        String circleIdStr = circleIds.toString().replace("[", "").replace("]", "");
        String dateFilter = getDateFilter(period);

        return jdbcTemplate.queryForList(
            "SELECT a.album_id, a.title, a.cover_url, c.name AS circle_name, " +
            "COALESCE(f.fav_count, 0) AS favorite_count " +
            "FROM albums a " +
            "JOIN album_circles ac ON a.album_id = ac.album_id " +
            "LEFT JOIN circles c ON ac.circle_id = c.circle_id " +
            "LEFT JOIN (SELECT album_id, COUNT(*) AS fav_count FROM favorites GROUP BY album_id) f ON a.album_id = f.album_id " +
            "WHERE ac.circle_id IN (" + circleIdStr + ") " +
            "AND a.publish_date >= " + dateFilter + " " +
            "ORDER BY favorite_count DESC LIMIT " + limit);
    }

    public List<Map<String, Object>> getProTopCircles(Integer userId, String period, int limit) {
        return Collections.emptyList();
    }

    public List<Map<String, Object>> getProTagDistribution(Integer userId) {
        List<Integer> circleIds = circleMapper.selectCircleIdsByUserId(userId);
        if (circleIds.isEmpty()) return Collections.emptyList();
        String circleIdStr = circleIds.toString().replace("[", "").replace("]", "");

        return jdbcTemplate.queryForList(
            "SELECT t.tag_id, t.name, COUNT(at2.album_id) AS album_count " +
            "FROM tags t " +
            "JOIN album_tags at2 ON t.tag_id = at2.tag_id " +
            "JOIN album_circles ac ON at2.album_id = ac.album_id " +
            "WHERE ac.circle_id IN (" + circleIdStr + ") " +
            "GROUP BY t.tag_id, t.name " +
            "ORDER BY album_count DESC LIMIT 30");
    }

    private String getDateFilter(String period) {
        return switch (period) {
            case "week" -> "CURRENT_DATE - INTERVAL '7 days'";
            case "month" -> "CURRENT_DATE - INTERVAL '30 days'";
            default -> "'2000-01-01'";
        };
    }

    private void applyUrlPrefix(Map<String, Object> item, String field) {
        Object value = item.get(field);
        if (value instanceof String url && !url.isBlank() && !url.startsWith("http") && !url.startsWith("/minio")) {
            item.put(field, "/minio/indietracks/" + url);
        }
    }
}
