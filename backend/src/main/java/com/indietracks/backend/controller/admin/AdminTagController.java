package com.indietracks.backend.controller.admin;

import com.indietracks.backend.service.admin.AdminTagService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin/tags")
public class AdminTagController {

    private final AdminTagService tagService;

    public AdminTagController(AdminTagService tagService) {
        this.tagService = tagService;
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> getTags(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "50") int page_size,
            @RequestParam(required = false) String search) {
        return ResponseEntity.ok(tagService.getTags(page, page_size, search));
    }

    @PostMapping
    public ResponseEntity<?> createTag(@RequestBody Map<String, String> body) {
        tagService.createTag(body.get("name"));
        return ResponseEntity.ok(Map.of("message", "标签创建成功"));
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateTag(@PathVariable Integer id, @RequestBody Map<String, String> body) {
        tagService.updateTag(id, body.get("name"));
        return ResponseEntity.ok(Map.of("message", "标签更新成功"));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteTag(@PathVariable Integer id) {
        tagService.deleteTag(id);
        return ResponseEntity.ok(Map.of("message", "标签删除成功"));
    }
}
