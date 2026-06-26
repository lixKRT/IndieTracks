package com.indietracks.backend.controller.admin;

import com.indietracks.backend.service.admin.AdminCircleService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/** 管理后台社团管理 — 列表、详情、更新、删除 */
@RestController
@RequestMapping("/api/admin/circles")
public class AdminCircleController {

    private final AdminCircleService circleService;

    public AdminCircleController(AdminCircleService circleService) {
        this.circleService = circleService;
    }

    /**
     * 分页获取社团列表.
     *
     * @param page      页码，默认 1
     * @param page_size 每页条数，默认 20
     * @param search    搜索关键词（可选），按社团名模糊匹配
     * @return 分页结果 Map，包含 records 列表和 total 总数
     */
    @GetMapping
    public ResponseEntity<Map<String, Object>> getCircles(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int page_size,
            @RequestParam(required = false) String search) {
        return ResponseEntity.ok(circleService.getCircles(page, page_size, search));
    }

    /**
     * 获取社团详情.
     *
     * @param id 社团 ID
     * @return 社团详细信息
     */
    @GetMapping("/{id}")
    public ResponseEntity<?> getCircle(@PathVariable Integer id) {
        return ResponseEntity.ok(circleService.getCircleDetail(id));
    }

    /**
     * 更新社团信息.
     *
     * @param id   社团 ID
     * @param body 请求体，包含需要更新的字段
     * @return 更新成功消息
     */
    @PutMapping("/{id}")
    public ResponseEntity<?> updateCircle(@PathVariable Integer id, @RequestBody Map<String, Object> body) {
        circleService.updateCircle(id, body);
        return ResponseEntity.ok(Map.of("message", "社团更新成功"));
    }

    /**
     * 删除社团.
     *
     * @param id 社团 ID
     * @return 删除成功消息
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteCircle(@PathVariable Integer id) {
        circleService.deleteCircle(id);
        return ResponseEntity.ok(Map.of("message", "社团删除成功"));
    }
}
