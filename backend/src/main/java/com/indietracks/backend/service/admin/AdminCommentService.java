package com.indietracks.backend.service.admin;

import com.indietracks.backend.mapper.CircleMapper;
import com.indietracks.backend.mapper.CommentMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class AdminCommentService {

    private final CommentMapper commentMapper;
    private final CircleMapper circleMapper;
    private final JdbcTemplate jdbcTemplate;

    public AdminCommentService(CommentMapper commentMapper, CircleMapper circleMapper, JdbcTemplate jdbcTemplate) {
        this.commentMapper = commentMapper;
        this.circleMapper = circleMapper;
        this.jdbcTemplate = jdbcTemplate;
    }

    public Map<String, Object> getStaffComments(int page, int pageSize) {
        int offset = (page - 1) * pageSize;

        List<Map<String, Object>> comments = jdbcTemplate.queryForList(
            "SELECT cm.comment_id, cm.content, cm.created_at, " +
            "u.user_id, u.username, u.avatar_url, " +
            "a.album_id, a.title AS album_title " +
            "FROM comments cm " +
            "LEFT JOIN users u ON cm.user_id = u.user_id " +
            "LEFT JOIN albums a ON cm.album_id = a.album_id " +
            "ORDER BY cm.created_at DESC " +
            "LIMIT " + pageSize + " OFFSET " + offset);

        // 应用 URL 前缀
        for (Map<String, Object> comment : comments) {
            applyUrlPrefix(comment, "avatar_url");
        }

        Integer total = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM comments", Integer.class);

        Map<String, Object> result = new HashMap<>();
        result.put("data", comments);
        result.put("total", total != null ? total : 0);
        result.put("page", page);
        result.put("page_size", pageSize);
        return result;
    }

    public Map<String, Object> getProComments(Integer userId, int page, int pageSize) {
        List<Integer> circleIds = circleMapper.selectCircleIdsByUserId(userId);
        if (circleIds.isEmpty()) {
            Map<String, Object> result = new HashMap<>();
            result.put("data", List.of());
            result.put("total", 0);
            result.put("page", 1);
            result.put("page_size", pageSize);
            return result;
        }

        String circleIdStr = circleIds.toString().replace("[", "").replace("]", "");
        int offset = (page - 1) * pageSize;

        List<Map<String, Object>> comments = jdbcTemplate.queryForList(
            "SELECT cm.comment_id, cm.content, cm.created_at, " +
            "u.user_id, u.username, u.avatar_url, " +
            "a.album_id, a.title AS album_title " +
            "FROM comments cm " +
            "LEFT JOIN users u ON cm.user_id = u.user_id " +
            "LEFT JOIN albums a ON cm.album_id = a.album_id " +
            "JOIN album_circles ac ON cm.album_id = ac.album_id " +
            "WHERE ac.circle_id IN (" + circleIdStr + ") " +
            "ORDER BY cm.created_at DESC " +
            "LIMIT " + pageSize + " OFFSET " + offset);

        // 应用 URL 前缀
        for (Map<String, Object> comment : comments) {
            applyUrlPrefix(comment, "avatar_url");
        }

        Integer total = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM comments cm JOIN album_circles ac ON cm.album_id = ac.album_id WHERE ac.circle_id IN (" + circleIdStr + ")",
            Integer.class);

        Map<String, Object> result = new HashMap<>();
        result.put("data", comments);
        result.put("total", total != null ? total : 0);
        result.put("page", page);
        result.put("page_size", pageSize);
        return result;
    }

    public boolean canUserDeleteComment(Integer userId, Integer commentId) {
        List<Integer> circleIds = circleMapper.selectCircleIdsByUserId(userId);
        if (circleIds.isEmpty()) return false;
        String circleIdStr = circleIds.toString().replace("[", "").replace("]", "");

        Integer count = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM comments cm JOIN album_circles ac ON cm.album_id = ac.album_id " +
            "WHERE cm.comment_id = " + commentId + " AND ac.circle_id IN (" + circleIdStr + ")",
            Integer.class);
        return count != null && count > 0;
    }

    public void deleteComment(Integer commentId) {
        commentMapper.deleteById(commentId);
    }

    private void applyUrlPrefix(Map<String, Object> item, String field) {
        Object value = item.get(field);
        if (value instanceof String url && !url.isBlank() && !url.startsWith("http") && !url.startsWith("/minio")) {
            item.put(field, "/minio/indietracks/" + url);
        }
    }
}
