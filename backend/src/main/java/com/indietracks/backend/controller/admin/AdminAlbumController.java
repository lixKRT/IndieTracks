package com.indietracks.backend.controller.admin;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.entity.User;
import com.indietracks.backend.mapper.UserMapper;
import com.indietracks.backend.service.admin.AdminAlbumService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** 管理后台专辑管理 — CRUD、标签管理、曲目管理，pro 用户仅限所属社团的专辑 */
@RestController
@RequestMapping("/api/admin/albums")
public class AdminAlbumController {

    private final AdminAlbumService albumService;
    private final UserMapper userMapper;

    public AdminAlbumController(AdminAlbumService albumService, UserMapper userMapper) {
        this.albumService = albumService;
        this.userMapper = userMapper;
    }

    /**
     * 分页获取专辑列表.
     * <p>pro 用户仅返回所属社团的专辑，staff 用户可查看全部并支持按社团筛选.</p>
     *
     * @param userId    当前登录用户 ID
     * @param page      页码，默认 1
     * @param page_size 每页条数，默认 20
     * @param search    搜索关键词（可选），按专辑名模糊匹配
     * @param circle_id 社团 ID 筛选（可选），仅 staff 角色生效
     * @return 分页结果 Map，包含 records 列表和 total 总数
     */
    @GetMapping
    public ResponseEntity<Map<String, Object>> getAlbums(
            @CurrentUser Integer userId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int page_size,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) Integer circle_id) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role())) {
            return ResponseEntity.ok(albumService.getProAlbums(userId, page, page_size, search));
        }
        return ResponseEntity.ok(albumService.getStaffAlbums(page, page_size, search, circle_id));
    }

    /**
     * 创建新专辑.
     * <p>body 需包含 circle_id 等字段。pro 用户仅能为所属社团创建专辑，否则返回 403.</p>
     *
     * @param userId 当前登录用户 ID
     * @param body   请求体，需包含 circle_id、title 等专辑信息
     * @return 创建成功消息，或 403 无权访问错误
     */
    @PostMapping
    public ResponseEntity<?> createAlbum(@CurrentUser Integer userId, @RequestBody Map<String, Object> body) {
        User user = userMapper.selectById(userId);
        // Pro 用户只能为所属社团创建专辑
        if ("pro".equals(user.getUser_role())) {
            Integer circleId = (Integer) body.get("circle_id");
            if (!albumService.isUserInCircle(userId, circleId)) {
                return ResponseEntity.status(403).body(Map.of("error", "无权为该社团创建专辑"));
            }
        }
        albumService.createAlbum(body);
        return ResponseEntity.ok(Map.of("message", "专辑创建成功"));
    }

    /**
     * 更新专辑信息.
     * <p>pro 用户只能编辑所属社团的专辑，否则返回 403.</p>
     *
     * @param userId 当前登录用户 ID
     * @param id     专辑 ID
     * @param body   请求体，包含需要更新的字段
     * @return 更新成功消息，或 403 无权访问错误
     */
    @PutMapping("/{id}")
    public ResponseEntity<?> updateAlbum(@CurrentUser Integer userId, @PathVariable Integer id,
                                         @RequestBody Map<String, Object> body) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role()) && !albumService.canUserEditAlbum(userId, id)) {
            return ResponseEntity.status(403).body(Map.of("error", "无权编辑该专辑"));
        }
        albumService.updateAlbum(id, body);
        return ResponseEntity.ok(Map.of("message", "专辑更新成功"));
    }

    /**
     * 删除专辑.
     * <p>pro 用户只能删除所属社团的专辑，否则返回 403.</p>
     *
     * @param userId 当前登录用户 ID
     * @param id     专辑 ID
     * @return 删除成功消息，或 403 无权访问错误
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteAlbum(@CurrentUser Integer userId, @PathVariable Integer id) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role()) && !albumService.canUserEditAlbum(userId, id)) {
            return ResponseEntity.status(403).body(Map.of("error", "无权删除该专辑"));
        }
        albumService.deleteAlbum(id);
        return ResponseEntity.ok(Map.of("message", "专辑删除成功"));
    }

    // ===== 标签管理 =====

    /**
     * 为专辑添加标签.
     *
     * @param id   专辑 ID
     * @param body 请求体，包含 name 字段（标签名称）
     * @return 添加成功消息
     */
    @PostMapping("/{id}/tags")
    public ResponseEntity<?> addTag(@PathVariable Integer id, @RequestBody Map<String, String> body) {
        albumService.addAlbumTag(id, body.get("name"));
        return ResponseEntity.ok(Map.of("message", "标签添加成功"));
    }

    /**
     * 移除专辑标签.
     *
     * @param id    专辑 ID
     * @param tagId 标签 ID
     * @return 删除成功消息
     */
    @DeleteMapping("/{id}/tags/{tagId}")
    public ResponseEntity<?> removeTag(@PathVariable Integer id, @PathVariable Integer tagId) {
        albumService.removeAlbumTag(id, tagId);
        return ResponseEntity.ok(Map.of("message", "标签删除成功"));
    }

    // ===== 曲目管理 =====

    /**
     * 删除专辑中的曲目.
     *
     * @param id      专辑 ID
     * @param trackId 曲目 ID
     * @return 删除成功消息
     */
    @DeleteMapping("/{id}/tracks/{trackId}")
    public ResponseEntity<?> deleteTrack(@PathVariable Integer id, @PathVariable Integer trackId) {
        albumService.deleteTrack(trackId);
        return ResponseEntity.ok(Map.of("message", "曲目删除成功"));
    }
}
