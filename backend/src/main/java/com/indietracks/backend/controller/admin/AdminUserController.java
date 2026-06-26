package com.indietracks.backend.controller.admin;

import com.indietracks.backend.service.admin.AdminUserService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/** 管理后台用户管理 — 列表、更新、删除 */
@RestController
@RequestMapping("/api/admin/users")
public class AdminUserController {

    private final AdminUserService userService;

    public AdminUserController(AdminUserService userService) {
        this.userService = userService;
    }

    /**
     * 分页获取用户列表.
     *
     * @param page      页码，默认 1
     * @param page_size 每页条数，默认 20
     * @param search    搜索关键词（可选），按用户名或邮箱模糊匹配
     * @param role      角色筛选（可选），可选值: normal、pro、staff
     * @return 分页结果 Map，包含 records 列表和 total 总数
     */
    @GetMapping
    public ResponseEntity<Map<String, Object>> getUsers(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int page_size,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String role) {
        return ResponseEntity.ok(userService.getUsers(page, page_size, search, role));
    }

    /**
     * 更新用户信息.
     *
     * @param id   用户 ID
     * @param body 请求体，包含需要更新的字段（如 role、nickname 等）
     * @return 更新成功消息
     */
    @PutMapping("/{id}")
    public ResponseEntity<?> updateUser(@PathVariable Integer id, @RequestBody Map<String, Object> body) {
        userService.updateUser(id, body);
        return ResponseEntity.ok(Map.of("message", "用户更新成功"));
    }

    /**
     * 删除用户.
     *
     * @param id 用户 ID
     * @return 删除成功消息
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteUser(@PathVariable Integer id) {
        userService.deleteUser(id);
        return ResponseEntity.ok(Map.of("message", "用户删除成功"));
    }
}
