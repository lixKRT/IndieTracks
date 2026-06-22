package com.indietracks.backend.service.admin;

import com.indietracks.backend.entity.Circle;
import com.indietracks.backend.mapper.CircleMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class AdminCircleService {

    private final CircleMapper circleMapper;
    private final JdbcTemplate jdbcTemplate;
    private final UrlPresignHelper urlPresign;

    public AdminCircleService(CircleMapper circleMapper, JdbcTemplate jdbcTemplate, UrlPresignHelper urlPresign) {
        this.circleMapper = circleMapper;
        this.jdbcTemplate = jdbcTemplate;
        this.urlPresign = urlPresign;
    }

    public Map<String, Object> getCircles(int page, int pageSize, String search) {
        int offset = (page - 1) * pageSize;
        String whereClause = "";
        if (search != null && !search.isBlank()) {
            whereClause = " WHERE c.name ILIKE '%" + search + "%'";
        }

        List<Map<String, Object>> circles = jdbcTemplate.queryForList(
            "SELECT c.circle_id, c.name, c.logo_url, c.description, c.member_count, " +
            "COALESCE(ac.album_count, 0) AS album_count " +
            "FROM circles c " +
            "LEFT JOIN (SELECT circle_id, COUNT(*) AS album_count FROM album_circles GROUP BY circle_id) ac " +
            "ON c.circle_id = ac.circle_id" +
            whereClause +
            " ORDER BY c.circle_id " +
            "LIMIT " + pageSize + " OFFSET " + offset);

        // 应用 URL 前缀
        for (Map<String, Object> circle : circles) {
            applyUrlPrefix(circle, "logo_url");
        }

        Integer total = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM circles c" + whereClause.replace("c.name", "name"), Integer.class);

        Map<String, Object> result = new HashMap<>();
        result.put("data", circles);
        result.put("total", total != null ? total : 0);
        result.put("page", page);
        result.put("page_size", pageSize);
        return result;
    }

    public Map<String, Object> getCircleDetail(Integer circleId) {
        Circle circle = circleMapper.selectById(circleId);
        if (circle == null) return null;

        Map<String, Object> detail = new HashMap<>();
        detail.put("circle_id", circle.getCircle_id());
        detail.put("name", circle.getName());
        detail.put("logo_url", applyPrefix(circle.getLogo_url()));
        detail.put("description", circle.getDescription());
        detail.put("member_count", circle.getMember_count());

        List<Map<String, Object>> members = jdbcTemplate.queryForList(
            "SELECT u.user_id, u.username, u.avatar_url, u.user_role " +
            "FROM users u JOIN user_circles uc ON u.user_id = uc.user_id " +
            "WHERE uc.circle_id = " + circleId + " ORDER BY u.user_id");
        for (Map<String, Object> member : members) {
            applyUrlPrefix(member, "avatar_url");
        }
        detail.put("members", members);

        return detail;
    }

    private void applyUrlPrefix(Map<String, Object> item, String field) {
        Object value = item.get(field);
        if (value instanceof String url && !url.isBlank() && !url.startsWith("http")) {
            item.put(field, "/minio/indietracks/" + url);
        }
    }

    private String applyPrefix(String url) {
        if (url != null && !url.isBlank() && !url.startsWith("http")) {
            return "/minio/indietracks/" + url;
        }
        return url;
    }

    public void updateCircle(Integer circleId, Map<String, Object> body) {
        Circle circle = circleMapper.selectById(circleId);
        if (circle == null) return;
        if (body.containsKey("name")) circle.setName((String) body.get("name"));
        if (body.containsKey("description")) circle.setDescription((String) body.get("description"));
        if (body.containsKey("logo_url")) circle.setLogo_url((String) body.get("logo_url"));
        circleMapper.updateById(circle);
    }

    public void deleteCircle(Integer circleId) {
        circleMapper.deleteById(circleId);
    }
}
