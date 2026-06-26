package com.indietracks.backend.controller.admin;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.entity.User;
import com.indietracks.backend.mapper.UserMapper;
import com.indietracks.backend.service.admin.AdminCommentService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * 管理后台 — 评论管理控制器。
 * <p>
 * 提供评论列表查询与删除功能，根据当前用户角色实施差异化权限：
 * <ul>
 *   <li><b>pro</b>（音乐人）：只能查看和删除自己专辑下的评论</li>
 *   <li><b>staff</b>（管理员）：可查看和删除所有评论</li>
 * </ul>
 * 基础路径: {@code /api/admin/comments}
 * </p>
 */
@RestController
@RequestMapping("/api/admin/comments")
public class AdminCommentController {

    private final AdminCommentService commentService;
    private final UserMapper userMapper;

    /**
     * 构造器注入。
     *
     * @param commentService 评论管理业务服务
     * @param userMapper     用户数据访问，用于根据 ID 查询当前用户角色
     */
    public AdminCommentController(AdminCommentService commentService, UserMapper userMapper) {
        this.commentService = commentService;
        this.userMapper = userMapper;
    }

    /**
     * 分页获取评论列表。
     * <p>
     * 根据当前用户角色返回不同范围的数据：
     * <ul>
     *   <li>pro — 仅返回其拥有专辑关联的评论</li>
     *   <li>staff — 返回全部评论</li>
     * </ul>
     * 返回 Map 而非单条记录，前端可直接用于替换当前分页数据。
     * </p>
     *
     * @param userId    当前登录用户 ID（由 {@link CurrentUser} 注解从 JWT 中提取）
     * @param page      页码，默认 1
     * @param page_size 每页条数，默认 20
     * @return 包含分页评论数据的 Map（含 list、total 等字段）
     */
    @GetMapping
    public ResponseEntity<Map<String, Object>> getComments(
            @CurrentUser Integer userId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int page_size) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role())) {
            return ResponseEntity.ok(commentService.getProComments(userId, page, page_size));
        }
        return ResponseEntity.ok(commentService.getStaffComments(page, page_size));
    }

    /**
     * 删除指定评论。
     * <p>
     * 权限校验逻辑：
     * <ul>
     *   <li>pro — 仅当评论所属专辑归该用户所有时才允许删除，否则返回 403</li>
     *   <li>staff — 直接删除，无额外限制</li>
     * </ul>
     * </p>
     *
     * @param userId 当前登录用户 ID（由 {@link CurrentUser} 注解从 JWT 中提取）
     * @param id     要删除的评论 ID
     * @return 操作成功返回 200 + 成功消息；权限不足返回 403 + 错误消息
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteComment(@CurrentUser Integer userId, @PathVariable Integer id) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role()) && !commentService.canUserDeleteComment(userId, id)) {
            return ResponseEntity.status(403).body(Map.of("error", "无权删除该评论"));
        }
        commentService.deleteComment(id);
        return ResponseEntity.ok(Map.of("message", "评论删除成功"));
    }
}
