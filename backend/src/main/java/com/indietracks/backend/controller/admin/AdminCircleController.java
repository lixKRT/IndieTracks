package com.indietracks.backend.controller.admin;

import com.indietracks.backend.service.admin.AdminCircleService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/admin/circles")
public class AdminCircleController {

    private final AdminCircleService circleService;

    public AdminCircleController(AdminCircleService circleService) {
        this.circleService = circleService;
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> getCircles(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int page_size,
            @RequestParam(required = false) String search) {
        return ResponseEntity.ok(circleService.getCircles(page, page_size, search));
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getCircle(@PathVariable Integer id) {
        return ResponseEntity.ok(circleService.getCircleDetail(id));
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateCircle(@PathVariable Integer id, @RequestBody Map<String, Object> body) {
        circleService.updateCircle(id, body);
        return ResponseEntity.ok(Map.of("message", "社团更新成功"));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteCircle(@PathVariable Integer id) {
        circleService.deleteCircle(id);
        return ResponseEntity.ok(Map.of("message", "社团删除成功"));
    }
}
