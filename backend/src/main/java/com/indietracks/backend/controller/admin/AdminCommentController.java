package com.indietracks.backend.controller.admin;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.entity.User;
import com.indietracks.backend.mapper.UserMapper;
import com.indietracks.backend.service.admin.AdminCommentService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/admin/comments")
public class AdminCommentController {

    private final AdminCommentService commentService;
    private final UserMapper userMapper;

    public AdminCommentController(AdminCommentService commentService, UserMapper userMapper) {
        this.commentService = commentService;
        this.userMapper = userMapper;
    }

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
