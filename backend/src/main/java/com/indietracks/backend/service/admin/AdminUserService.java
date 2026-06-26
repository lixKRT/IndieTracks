package com.indietracks.backend.service.admin;

import com.indietracks.backend.entity.User;
import com.indietracks.backend.mapper.UserMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** 管理后台 — 用户管理服务：分页查询、修改角色、删除用户 */
@Service
public class AdminUserService {

    private final UserMapper userMapper;
    private final JdbcTemplate jdbcTemplate; // 用于手动拼接带筛选条件的复杂 SQL
    private final UrlPresignHelper urlPresign;

    public AdminUserService(UserMapper userMapper, JdbcTemplate jdbcTemplate, UrlPresignHelper urlPresign) {
        this.userMapper = userMapper;
        this.jdbcTemplate = jdbcTemplate;
        this.urlPresign = urlPresign;
    }

    /** @param role 可选筛选，可选值: normal, pro, staff */
    public Map<String, Object> getUsers(int page, int pageSize, String search, String role) {
        int offset = (page - 1) * pageSize;
        StringBuilder whereClause = new StringBuilder(" WHERE 1=1");
        if (search != null && !search.isBlank()) {
            whereClause.append(" AND u.username ILIKE '%").append(search).append("%'");
        }
        if (role != null && !role.isBlank()) {
            whereClause.append(" AND u.user_role = '").append(role).append("'");
        }

        List<Map<String, Object>> users = jdbcTemplate.queryForList(
            "SELECT u.user_id, u.username, u.email, u.avatar_url, u.user_role, u.created_at " +
            "FROM users u" + whereClause +
            " ORDER BY u.user_id DESC " +
            "LIMIT " + pageSize + " OFFSET " + offset);

        // MinIO 对象 Key → Nginx 代理路径前缀
        for (Map<String, Object> user : users) {
            Object avatarUrl = user.get("avatar_url");
            if (avatarUrl instanceof String url && !url.isBlank() && !url.startsWith("http")) {
                user.put("avatar_url", "/minio/indietracks/" + url);
            }
        }

        Integer total = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM users u" + whereClause, Integer.class);

        Map<String, Object> result = new HashMap<>();
        result.put("data", users);
        result.put("total", total != null ? total : 0);
        result.put("page", page);
        result.put("page_size", pageSize);
        return result;
    }

    /** 仅允许修改 user_role 字段，其余字段忽略 */
    public void updateUser(Integer userId, Map<String, Object> body) {
        User user = userMapper.selectById(userId);
        if (user == null) return;
        if (body.containsKey("user_role")) {
            user.setUser_role((String) body.get("user_role"));
        }
        userMapper.updateById(user);
    }

    public void deleteUser(Integer userId) {
        userMapper.deleteById(userId);
    }
}
