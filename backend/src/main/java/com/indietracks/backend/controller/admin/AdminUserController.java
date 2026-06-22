package com.indietracks.backend.controller.admin;

import com.indietracks.backend.service.admin.AdminUserService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/admin/users")
public class AdminUserController {

    private final AdminUserService userService;

    public AdminUserController(AdminUserService userService) {
        this.userService = userService;
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> getUsers(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int page_size,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String role) {
        return ResponseEntity.ok(userService.getUsers(page, page_size, search, role));
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateUser(@PathVariable Integer id, @RequestBody Map<String, Object> body) {
        userService.updateUser(id, body);
        return ResponseEntity.ok(Map.of("message", "用户更新成功"));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteUser(@PathVariable Integer id) {
        userService.deleteUser(id);
        return ResponseEntity.ok(Map.of("message", "用户删除成功"));
    }
}
