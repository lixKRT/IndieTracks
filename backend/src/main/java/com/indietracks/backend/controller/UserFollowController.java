package com.indietracks.backend.controller;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.service.UserFollowService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/user-follows")
public class UserFollowController {

    private final UserFollowService userFollowService;

    public UserFollowController(UserFollowService userFollowService) {
        this.userFollowService = userFollowService;
    }

    @PostMapping("/{userId}")
    public ResponseEntity<?> follow(@PathVariable Integer userId, @CurrentUser Integer currentUserId) {
        if (currentUserId.equals(userId)) {
            return ResponseEntity.badRequest().body(Map.of("error", "不能关注自己"));
        }
        userFollowService.follow(currentUserId, userId);
        return ResponseEntity.ok(Map.of("message", "已关注"));
    }

    @DeleteMapping("/{userId}")
    public ResponseEntity<?> unfollow(@PathVariable Integer userId, @CurrentUser Integer currentUserId) {
        userFollowService.unfollow(currentUserId, userId);
        return ResponseEntity.ok(Map.of("message", "已取消关注"));
    }

    @GetMapping("/{userId}/status")
    public ResponseEntity<Map<String, Boolean>> checkFollow(@PathVariable Integer userId, @CurrentUser Integer currentUserId) {
        boolean followed = userFollowService.isFollowing(currentUserId, userId);
        return ResponseEntity.ok(Map.of("followed", followed));
    }
}
