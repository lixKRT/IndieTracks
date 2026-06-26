package com.indietracks.backend.controller.admin;

import com.indietracks.backend.service.admin.AdminTagService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 管理后台 — 标签管理控制器。
 * <p>
 * 提供标签的完整 CRUD 操作（增删改查），供管理员在后台维护音乐标签体系。
 * 基础路径: {@code /api/admin/tags}
 * </p>
 */
@RestController
@RequestMapping("/api/admin/tags")
public class AdminTagController {

    private final AdminTagService tagService;

    /**
     * 构造器注入。
     *
     * @param tagService 标签管理业务服务
     */
    public AdminTagController(AdminTagService tagService) {
        this.tagService = tagService;
    }

    /**
     * 分页查询标签列表。
     * <p>
     * 支持按关键字模糊搜索标签名称；不传 search 参数时返回全部标签。
     * </p>
     *
     * @param page      页码，默认 1
     * @param page_size 每页条数，默认 50
     * @param search    可选的搜索关键字，按标签名称模糊匹配
     * @return 包含分页标签数据的 Map（含 list、total 等字段）
     */
    @GetMapping
    public ResponseEntity<Map<String, Object>> getTags(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "50") int page_size,
            @RequestParam(required = false) String search) {
        return ResponseEntity.ok(tagService.getTags(page, page_size, search));
    }

    /**
     * 新建标签。
     *
     * @param body 请求体，必须包含 {@code name} 字段（标签名称）
     * @return 操作成功的提示消息
     */
    @PostMapping
    public ResponseEntity<?> createTag(@RequestBody Map<String, String> body) {
        tagService.createTag(body.get("name"));
        return ResponseEntity.ok(Map.of("message", "标签创建成功"));
    }

    /**
     * 更新指定标签的名称。
     *
     * @param id   要更新的标签 ID（路径参数）
     * @param body 请求体，必须包含 {@code name} 字段（新标签名称）
     * @return 操作成功的提示消息
     */
    @PutMapping("/{id}")
    public ResponseEntity<?> updateTag(@PathVariable Integer id, @RequestBody Map<String, String> body) {
        tagService.updateTag(id, body.get("name"));
        return ResponseEntity.ok(Map.of("message", "标签更新成功"));
    }

    /**
     * 删除指定标签。
     *
     * @param id 要删除的标签 ID（路径参数）
     * @return 操作成功的提示消息
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteTag(@PathVariable Integer id) {
        tagService.deleteTag(id);
        return ResponseEntity.ok(Map.of("message", "标签删除成功"));
    }
}
