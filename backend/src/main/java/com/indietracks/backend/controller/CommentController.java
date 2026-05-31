package com.indietracks.backend.controller;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.dto.CommentRequest;
import com.indietracks.backend.service.CommentService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/comments")
public class CommentController {

    private final CommentService commentService;

    public CommentController(CommentService commentService) {
        this.commentService = commentService;
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateComment(@PathVariable Integer id,
                                           @Valid @RequestBody CommentRequest req,
                                           @CurrentUser Integer userId) {
        boolean ok = commentService.updateComment(id, userId, req.getContent());
        if (!ok) return ResponseEntity.status(403).body(Map.of("error", "只能编辑自己的评论"));
        return ResponseEntity.ok(Map.of("message", "已更新"));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteComment(@PathVariable Integer id, @CurrentUser Integer userId) {
        boolean ok = commentService.deleteComment(id, userId);
        if (!ok) return ResponseEntity.status(403).body(Map.of("error", "只能删除自己的评论"));
        return ResponseEntity.ok(Map.of("message", "已删除"));
    }
}
