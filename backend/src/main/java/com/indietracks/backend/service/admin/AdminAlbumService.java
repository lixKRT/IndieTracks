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

/**
 * 管理端专辑服务。
 * <p>
 * 根据管理员角色（Staff / Pro）提供不同范围的专辑查询能力：
 * <ul>
 *   <li><b>Staff</b> — 可查看和管理全量专辑</li>
 *   <li><b>Pro</b> — 仅可查看和管理所属社团的专辑</li>
 * </ul>
 * 同时提供专辑的 CRUD 操作、标签管理以及曲目删除功能。
 * </p>
 *
 * <h3>依赖说明</h3>
 * <ul>
 *   <li>{@link AlbumMapper} — 专辑实体及关联表的 CRUD</li>
 *   <li>{@link CircleMapper} — 社团与用户关联查询</li>
 *   <li>{@link UrlPresignHelper} — MinIO 对象 URL 预签名</li>
 *   <li>{@link JdbcTemplate} — 标签和曲目的原生 SQL 操作</li>
 * </ul>
 *
 * @see AlbumMapper
 * @see CircleMapper
 */
@Service
public class AdminAlbumService {

    private final AlbumMapper albumMapper;
    private final CircleMapper circleMapper;
    private final UrlPresignHelper urlPresign;
    private final JdbcTemplate jdbcTemplate;

    /**
     * 构造注入所有依赖。
     *
     * @param albumMapper   专辑 Mapper
     * @param circleMapper  社团 Mapper
     * @param urlPresign    URL 预签名工具
     * @param jdbcTemplate  Spring JDBC 模板（用于标签和曲目的原生 SQL）
     */
    public AdminAlbumService(AlbumMapper albumMapper, CircleMapper circleMapper, UrlPresignHelper urlPresign, JdbcTemplate jdbcTemplate) {
        this.albumMapper = albumMapper;
        this.circleMapper = circleMapper;
        this.urlPresign = urlPresign;
        this.jdbcTemplate = jdbcTemplate;
    }

    /**
     * 获取所有专辑（Staff 角色专用）。
     * <p>
     * 通过 MyBatis-Plus 分页查询全量专辑列表，支持按关键词搜索。
     * 结果按发布日期降序排列，封面 URL 会预签名。
     * </p>
     *
     * @param page     当前页码（从 1 开始）
     * @param pageSize 每页条数
     * @param search   搜索关键词（可为 {@code null}）
     * @param circleId 社团 ID 过滤（当前未使用，预留参数）
     * @return 包含 {@code data}、{@code total}、{@code page}、{@code page_size} 的分页结果 Map
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
     * 获取当前 Pro 用户所属社团的专辑列表。
     * <p>
     * 先查询用户关联的所有社团 ID，再查询这些社团下的全部专辑，
     * 支持按标题或社团名进行内存搜索过滤，并在应用层手动分页。
     * 若用户不属于任何社团，返回空结果。
     * </p>
     *
     * @param userId   当前用户 ID
     * @param page     当前页码（从 1 开始）
     * @param pageSize 每页条数
     * @param search   搜索关键词（可为 {@code null}）
     * @return 包含 {@code data}、{@code total}、{@code page}、{@code page_size} 的分页结果 Map
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
     * 检查用户是否属于指定社团。
     *
     * @param userId   用户 ID
     * @param circleId 社团 ID
     * @return {@code true} 表示用户在该社团中
     */
    public boolean isUserInCircle(Integer userId, Integer circleId) {
        List<Integer> circleIds = circleMapper.selectCircleIdsByUserId(userId);
        return circleIds.contains(circleId);
    }

    /**
     * 检查用户是否有权编辑指定专辑。
     * <p>
     * 通过比对用户所属社团与专辑关联社团是否存在交集来判断权限。
     * </p>
     *
     * @param userId  用户 ID
     * @param albumId 专辑 ID
     * @return {@code true} 表示用户有权编辑该专辑
     */
    public boolean canUserEditAlbum(Integer userId, Integer albumId) {
        List<Integer> userCircleIds = circleMapper.selectCircleIdsByUserId(userId);
        List<Integer> albumCircleIds = albumMapper.selectCircleIdsByAlbumId(albumId);
        return userCircleIds.stream().anyMatch(albumCircleIds::contains);
    }

    /**
     * 创建新专辑。
     * <p>
     * 从请求体 Map 中提取字段并构建 {@link Album} 实体，价格使用
     * {@link BigDecimal} 避免浮点精度丢失。创建成功后，若指定了社团 ID，
     * 会自动在 album_circles 关联表中插入记录。
     * </p>
     *
     * @param body 请求体，包含 {@code title}、{@code cover_url}、{@code price}、
     *             {@code info_title}、{@code info_content}、{@code circle_id} 等字段
     */
    public void createAlbum(Map<String, Object> body) {
        Album album = new Album();
        album.setTitle((String) body.get("title"));
        album.setCover_url((String) body.get("cover_url"));
        // BigDecimal 避免浮点精度丢失
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
     * 更新已有专辑信息。
     * <p>
     * 仅更新请求体中实际包含的字段（部分更新），未传入的字段保持不变。
     * 若专辑不存在则静默返回。
     * </p>
     *
     * @param albumId 专辑 ID
     * @param body    请求体，可包含 {@code title}、{@code cover_url}、{@code price}、
     *                {@code info_title}、{@code info_content} 中的任意字段
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
     * 删除专辑。
     * <p>
     * 注意：此操作不会级联删除关联的社团关系、标签或曲目记录，
     * 需根据数据库外键约束或业务需求另行处理。
     * </p>
     *
     * @param albumId 专辑 ID
     */
    public void deleteAlbum(Integer albumId) {
        albumMapper.deleteById(albumId);
    }

    /**
     * 为专辑添加标签（查找或创建）。
     * <p>
     * 使用 JdbcTemplate 实现 upsert 逻辑：
     * <ol>
     *   <li>尝试按名称查找已有标签</li>
     *   <li>若不存在则插入新标签记录</li>
     *   <li>在 album_tags 关联表中幂等插入（PostgreSQL ON CONFLICT DO NOTHING）</li>
     * </ol>
     * </p>
     *
     * @param albumId 专辑 ID
     * @param tagName 标签名称，为 {@code null} 或空白时静默跳过
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
        // 添加关联（ON CONFLICT DO NOTHING 幂等插入，PostgreSQL 语法）
        jdbcTemplate.update(
            "INSERT INTO album_tags (album_id, tag_id) VALUES (?, ?) ON CONFLICT DO NOTHING",
            albumId, tagId);
    }

    /**
     * 移除专辑与标签的关联关系。
     * <p>
     * 仅删除 album_tags 表中的关联记录，不会删除标签本身。
     * </p>
     *
     * @param albumId 专辑 ID
     * @param tagId   标签 ID
     */
    public void removeAlbumTag(Integer albumId, Integer tagId) {
        jdbcTemplate.update(
            "DELETE FROM album_tags WHERE album_id = ? AND tag_id = ?",
            albumId, tagId);
    }

    /**
     * 删除专辑下的单个曲目。
     * <p>
     * 直接从 work_files 表中物理删除指定 file_id 对应的记录。
     * </p>
     *
     * @param trackId 曲目文件 ID（对应 work_files.file_id）
     */
    public void deleteTrack(Integer trackId) {
        jdbcTemplate.update("DELETE FROM work_files WHERE file_id = ?", trackId);
    }
}
