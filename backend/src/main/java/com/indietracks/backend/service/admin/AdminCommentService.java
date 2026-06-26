package com.indietracks.backend.service.admin;

import com.indietracks.backend.mapper.CircleMapper;
import com.indietracks.backend.mapper.CommentMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** 管理后台 — 评论管理服务：staff 查看全部评论，pro 用户查看自己社团专辑的评论 */
@Service
public class AdminCommentService {

    private final CommentMapper commentMapper;
    private final CircleMapper circleMapper;
    private final JdbcTemplate jdbcTemplate; // 用于手动拼接带 JOIN 和聚合的复杂 SQL

    public AdminCommentService(CommentMapper commentMapper, CircleMapper circleMapper, JdbcTemplate jdbcTemplate) {
        this.commentMapper = commentMapper;
        this.circleMapper = circleMapper;
        this.jdbcTemplate = jdbcTemplate;
    }

    /** staff 查看全部评论，无社团范围限制 */
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

        // MinIO 对象 Key → Nginx 代理路径前缀
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

    /** pro 用户查看自己管理的社团关联专辑下的评论 */
    public Map<String, Object> getProComments(Integer userId, int page, int pageSize) {
        List<Integer> circleIds = circleMapper.selectCircleIdsByUserId(userId); // 用户管理的社团 ID 列表
        if (circleIds.isEmpty()) {
            Map<String, Object> result = new HashMap<>();
            result.put("data", List.of());
            result.put("total", 0);
            result.put("page", 1);
            result.put("page_size", pageSize);
            return result;
        }

        // List<Integer> → SQL IN 子句字符串（如 "1, 2, 3"）
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

        // MinIO 对象 Key → Nginx 代理路径前缀
        for (Map<String, Object> comment : comments) {
            applyUrlPrefix(comment, "avatar_url");
        }

        // count 查询也需要按社团范围过滤
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

    /** 校验 pro 用户是否有权删除评论（评论所属专辑须在其管理的社团下） */
    public boolean canUserDeleteComment(Integer userId, Integer commentId) {
        List<Integer> circleIds = circleMapper.selectCircleIdsByUserId(userId);
        if (circleIds.isEmpty()) return false;
        // List<Integer> → SQL IN 子句字符串（如 "1, 2, 3"）
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

    /** 将 MinIO 对象 Key 转为 Nginx 代理路径，已含完整 URL 的跳过 */
    private void applyUrlPrefix(Map<String, Object> item, String field) {
        Object value = item.get(field);
        if (value instanceof String url && !url.isBlank() && !url.startsWith("http") && !url.startsWith("/minio")) {
            item.put(field, "/minio/indietracks/" + url);
        }
    }
}
