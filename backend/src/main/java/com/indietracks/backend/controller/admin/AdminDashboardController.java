package com.indietracks.backend.controller.admin;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.entity.User;
import com.indietracks.backend.mapper.UserMapper;
import com.indietracks.backend.service.admin.AdminDashboardService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin/dashboard")
public class AdminDashboardController {

    private final AdminDashboardService dashboardService;
    private final UserMapper userMapper;

    public AdminDashboardController(AdminDashboardService dashboardService, UserMapper userMapper) {
        this.dashboardService = dashboardService;
        this.userMapper = userMapper;
    }

    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats(@CurrentUser Integer userId) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role())) {
            return ResponseEntity.ok(dashboardService.getProStats(userId));
        }
        return ResponseEntity.ok(dashboardService.getStaffStats());
    }

    @GetMapping("/trends")
    public ResponseEntity<Map<String, Object>> getTrends(
            @CurrentUser Integer userId,
            @RequestParam(defaultValue = "month") String period) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role())) {
            return ResponseEntity.ok(dashboardService.getProTrends(userId, period));
        }
        return ResponseEntity.ok(dashboardService.getStaffTrends(period));
    }

    @GetMapping("/top-albums")
    public ResponseEntity<List<Map<String, Object>>> getTopAlbums(
            @CurrentUser Integer userId,
            @RequestParam(defaultValue = "month") String period,
            @RequestParam(defaultValue = "50") int limit) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role())) {
            return ResponseEntity.ok(dashboardService.getProTopAlbums(userId, period, limit));
        }
        return ResponseEntity.ok(dashboardService.getStaffTopAlbums(period, limit));
    }

    @GetMapping("/top-circles")
    public ResponseEntity<List<Map<String, Object>>> getTopCircles(
            @CurrentUser Integer userId,
            @RequestParam(defaultValue = "month") String period,
            @RequestParam(defaultValue = "50") int limit) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role())) {
            return ResponseEntity.ok(dashboardService.getProTopCircles(userId, period, limit));
        }
        return ResponseEntity.ok(dashboardService.getStaffTopCircles(period, limit));
    }

    @GetMapping("/tag-distribution")
    public ResponseEntity<List<Map<String, Object>>> getTagDistribution(@CurrentUser Integer userId) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role())) {
            return ResponseEntity.ok(dashboardService.getProTagDistribution(userId));
        }
        return ResponseEntity.ok(dashboardService.getStaffTagDistribution());
    }
}
