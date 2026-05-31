package com.indietracks.backend.controller;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.service.CircleFollowService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/circle-follows")
public class CircleFollowController {

    private final CircleFollowService circleFollowService;

    public CircleFollowController(CircleFollowService circleFollowService) {
        this.circleFollowService = circleFollowService;
    }

    @PostMapping("/{circleId}")
    public ResponseEntity<?> follow(@PathVariable Integer circleId, @CurrentUser Integer userId) {
        circleFollowService.follow(userId, circleId);
        return ResponseEntity.ok(Map.of("message", "已关注"));
    }

    @DeleteMapping("/{circleId}")
    public ResponseEntity<?> unfollow(@PathVariable Integer circleId, @CurrentUser Integer userId) {
        circleFollowService.unfollow(userId, circleId);
        return ResponseEntity.ok(Map.of("message", "已取消关注"));
    }

    @GetMapping("/{circleId}/status")
    public ResponseEntity<Map<String, Boolean>> checkFollow(@PathVariable Integer circleId, @CurrentUser Integer userId) {
        boolean followed = circleFollowService.isFollowing(userId, circleId);
        return ResponseEntity.ok(Map.of("followed", followed));
    }
}
