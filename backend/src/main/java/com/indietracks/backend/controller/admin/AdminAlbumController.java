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

@RestController
@RequestMapping("/api/admin/albums")
public class AdminAlbumController {

    private final AdminAlbumService albumService;
    private final UserMapper userMapper;

    public AdminAlbumController(AdminAlbumService albumService, UserMapper userMapper) {
        this.albumService = albumService;
        this.userMapper = userMapper;
    }

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

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteAlbum(@CurrentUser Integer userId, @PathVariable Integer id) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role()) && !albumService.canUserEditAlbum(userId, id)) {
            return ResponseEntity.status(403).body(Map.of("error", "无权删除该专辑"));
        }
        albumService.deleteAlbum(id);
        return ResponseEntity.ok(Map.of("message", "专辑删除成功"));
    }
}
