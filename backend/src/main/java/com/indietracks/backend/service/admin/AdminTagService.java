package com.indietracks.backend.service.admin;

import com.indietracks.backend.entity.Tag;
import com.indietracks.backend.mapper.TagMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** 管理后台 — 标签管理服务：分页查询、增删改 */
@Service
public class AdminTagService {

    private final TagMapper tagMapper;
    private final JdbcTemplate jdbcTemplate; // 用于手动拼接带聚合函数的复杂 SQL

    public AdminTagService(TagMapper tagMapper, JdbcTemplate jdbcTemplate) {
        this.tagMapper = tagMapper;
        this.jdbcTemplate = jdbcTemplate;
    }

    public Map<String, Object> getTags(int page, int pageSize, String search) {
        int offset = (page - 1) * pageSize;
        String whereClause = "";
        if (search != null && !search.isBlank()) {
            whereClause = " WHERE t.name ILIKE '%" + search + "%'";
        }

        List<Map<String, Object>> tags = jdbcTemplate.queryForList(
            "SELECT t.tag_id, t.name, COUNT(at2.album_id) AS album_count " +
            "FROM tags t " +
            "LEFT JOIN album_tags at2 ON t.tag_id = at2.tag_id" +
            whereClause +
            " GROUP BY t.tag_id, t.name " +
            "ORDER BY t.tag_id " +
            "LIMIT " + pageSize + " OFFSET " + offset);

        // count 查询无表别名，需去掉 "t." 前缀
        Integer total = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM tags" + whereClause.replace("t.name", "name"), Integer.class);

        Map<String, Object> result = new HashMap<>();
        result.put("data", tags);
        result.put("total", total != null ? total : 0);
        result.put("page", page);
        result.put("page_size", pageSize);
        return result;
    }

    public void createTag(String name) {
        Tag tag = new Tag();
        tag.setName(name);
        tagMapper.insert(tag);
    }

    public void updateTag(Integer tagId, String name) {
        Tag tag = tagMapper.selectById(tagId);
        if (tag != null) {
            tag.setName(name);
            tagMapper.updateById(tag);
        }
    }

    public void deleteTag(Integer tagId) {
        tagMapper.deleteById(tagId);
    }
}
