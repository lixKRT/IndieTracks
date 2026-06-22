package com.indietracks.backend.service.admin;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.entity.Album;
import com.indietracks.backend.mapper.AlbumMapper;
import com.indietracks.backend.mapper.CircleMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class AdminAlbumService {

    private final AlbumMapper albumMapper;
    private final CircleMapper circleMapper;
    private final UrlPresignHelper urlPresign;
    private final JdbcTemplate jdbcTemplate;

    public AdminAlbumService(AlbumMapper albumMapper, CircleMapper circleMapper, UrlPresignHelper urlPresign, JdbcTemplate jdbcTemplate) {
        this.albumMapper = albumMapper;
        this.circleMapper = circleMapper;
        this.urlPresign = urlPresign;
        this.jdbcTemplate = jdbcTemplate;
    }

    /**
     * 获取所有专辑（Staff）
     */
    public Map<String, Object> getStaffAlbums(int page, int pageSize, String search, Integer circleId) {
        Page<AlbumListItem> pageParam = new Page<>(page, pageSize);
        IPage<AlbumListItem> result = albumMapper.selectAlbumList(pageParam, null, search, null, "publish_date_desc");
        urlPresign.presignAlbumList(result.getRecords());

        Map<String, Object> response = new HashMap<>();
        response.put("data", result.getRecords());
        response.put("total", result.getTotal());
        response.put("page", result.getCurrent());
        response.put("page_size", result.getSize());
        return response;
    }

    /**
     * 获取所属社团专辑（Pro）
     */
    public Map<String, Object> getProAlbums(Integer userId, int page, int pageSize, String search) {
        // 查询用户所属社团
        List<Integer> circleIds = circleMapper.selectCircleIdsByUserId(userId);
        if (circleIds.isEmpty()) {
            Map<String, Object> response = new HashMap<>();
            response.put("data", List.of());
            response.put("total", 0);
            response.put("page", 1);
            response.put("page_size", pageSize);
            return response;
        }

        // 查询所属社团的专辑
        List<AlbumListItem> allAlbums = albumMapper.selectAlbumsByCircleIds(circleIds);
        urlPresign.presignAlbumList(allAlbums);

        // 搜索过滤
        if (search != null && !search.isBlank()) {
            String searchLower = search.toLowerCase();
            allAlbums = allAlbums.stream()
                    .filter(a -> a.getTitle().toLowerCase().contains(searchLower)
                            || (a.getCircle_name() != null && a.getCircle_name().toLowerCase().contains(searchLower)))
                    .toList();
        }

        // 手动分页
        int total = allAlbums.size();
        int fromIndex = (page - 1) * pageSize;
        int toIndex = Math.min(fromIndex + pageSize, total);
        List<AlbumListItem> pageData = fromIndex < total ? allAlbums.subList(fromIndex, toIndex) : List.of();

        Map<String, Object> response = new HashMap<>();
        response.put("data", pageData);
        response.put("total", total);
        response.put("page", page);
        response.put("page_size", pageSize);
        return response;
    }

    /**
     * 检查用户是否在社团中
     */
    public boolean isUserInCircle(Integer userId, Integer circleId) {
        List<Integer> circleIds = circleMapper.selectCircleIdsByUserId(userId);
        return circleIds.contains(circleId);
    }

    /**
     * 检查用户是否可以编辑该专辑
     */
    public boolean canUserEditAlbum(Integer userId, Integer albumId) {
        List<Integer> userCircleIds = circleMapper.selectCircleIdsByUserId(userId);
        List<Integer> albumCircleIds = albumMapper.selectCircleIdsByAlbumId(albumId);
        return userCircleIds.stream().anyMatch(albumCircleIds::contains);
    }

    /**
     * 创建专辑
     */
    public void createAlbum(Map<String, Object> body) {
        Album album = new Album();
        album.setTitle((String) body.get("title"));
        album.setCover_url((String) body.get("cover_url"));
        album.setPrice(body.get("price") != null ? new BigDecimal(body.get("price").toString()) : BigDecimal.ZERO);
        album.setInfo_title((String) body.get("info_title"));
        album.setInfo_content((String) body.get("info_content"));
        albumMapper.insert(album);

        // 关联社团
        Integer circleId = (Integer) body.get("circle_id");
        if (circleId != null) {
            albumMapper.insertAlbumCircle(album.getAlbum_id(), circleId);
        }
    }

    /**
     * 更新专辑
     */
    public void updateAlbum(Integer albumId, Map<String, Object> body) {
        Album album = albumMapper.selectById(albumId);
        if (album == null) return;

        if (body.containsKey("title")) album.setTitle((String) body.get("title"));
        if (body.containsKey("cover_url")) album.setCover_url((String) body.get("cover_url"));
        if (body.containsKey("price")) album.setPrice(new BigDecimal(body.get("price").toString()));
        if (body.containsKey("info_title")) album.setInfo_title((String) body.get("info_title"));
        if (body.containsKey("info_content")) album.setInfo_content((String) body.get("info_content"));

        albumMapper.updateById(album);
    }

    /**
     * 删除专辑
     */
    public void deleteAlbum(Integer albumId) {
        albumMapper.deleteById(albumId);
    }

    /**
     * 添加专辑标签
     */
    public void addAlbumTag(Integer albumId, String tagName) {
        if (tagName == null || tagName.isBlank()) return;
        // 先查找或创建标签
        Integer tagId = jdbcTemplate.queryForObject(
            "SELECT tag_id FROM tags WHERE name = ?", Integer.class, tagName);
        if (tagId == null) {
            jdbcTemplate.update("INSERT INTO tags (name) VALUES (?)", tagName);
            tagId = jdbcTemplate.queryForObject(
                "SELECT tag_id FROM tags WHERE name = ?", Integer.class, tagName);
        }
        // 添加关联
        jdbcTemplate.update(
            "INSERT INTO album_tags (album_id, tag_id) VALUES (?, ?) ON CONFLICT DO NOTHING",
            albumId, tagId);
    }

    /**
     * 移除专辑标签
     */
    public void removeAlbumTag(Integer albumId, Integer tagId) {
        jdbcTemplate.update(
            "DELETE FROM album_tags WHERE album_id = ? AND tag_id = ?",
            albumId, tagId);
    }

    /**
     * 删除曲目
     */
    public void deleteTrack(Integer trackId) {
        jdbcTemplate.update("DELETE FROM work_files WHERE file_id = ?", trackId);
    }
}
