package com.indietracks.backend.controller.admin;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.entity.User;
import com.indietracks.backend.mapper.UserMapper;
import com.indietracks.backend.service.admin.AdminDashboardService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** 管理后台仪表盘 — 统计概览、趋势、排行榜，pro 看自身数据，staff 看全局 */
@RestController
@RequestMapping("/api/admin/dashboard")
public class AdminDashboardController {

    private final AdminDashboardService dashboardService;
    private final UserMapper userMapper;

    public AdminDashboardController(AdminDashboardService dashboardService, UserMapper userMapper) {
        this.dashboardService = dashboardService;
        this.userMapper = userMapper;
    }

    /**
     * 获取仪表盘统计数据.
     * <p>pro 用户返回自身所属社团的统计，staff 用户返回全局统计.</p>
     *
     * @param userId 当前登录用户 ID（由 @CurrentUser 注解从 JWT 中提取）
     * @return 统计数据 Map，包含专辑数、社团数、用户数等指标
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats(@CurrentUser Integer userId) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role())) {
            return ResponseEntity.ok(dashboardService.getProStats(userId));
        }
        return ResponseEntity.ok(dashboardService.getStaffStats());
    }

    /**
     * 获取统计数据趋势（按时间维度）.
     * <p>pro 用户返回自身社团趋势，staff 用户返回全局趋势.</p>
     *
     * @param userId 当前登录用户 ID
     * @param period 时间范围，可选值: week、month、year，默认 month
     * @return 趋势数据 Map，包含各时间点的统计值
     */
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

    /**
     * 获取专辑排行榜.
     * <p>pro 用户返回所属社团的专辑排行，staff 用户返回全局排行.</p>
     *
     * @param userId 当前登录用户 ID
     * @param period 时间范围，可选值: week、month、year，默认 month
     * @param limit  返回条数上限，默认 50
     * @return 专辑排行榜列表，按热度/销量等指标排序
     */
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

    /**
     * 获取社团排行榜.
     * <p>pro 用户返回自身相关社团排行，staff 用户返回全局排行.</p>
     *
     * @param userId 当前登录用户 ID
     * @param period 时间范围，可选值: week、month、year，默认 month
     * @param limit  返回条数上限，默认 50
     * @return 社团排行榜列表
     */
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

    /**
     * 获取标签分布统计.
     * <p>pro 用户返回所属社团的标签分布，staff 用户返回全局标签分布.</p>
     *
     * @param userId 当前登录用户 ID
     * @return 标签分布列表，每项包含标签名及其对应的专辑数量
     */
    @GetMapping("/tag-distribution")
    public ResponseEntity<List<Map<String, Object>>> getTagDistribution(@CurrentUser Integer userId) {
        User user = userMapper.selectById(userId);
        if ("pro".equals(user.getUser_role())) {
            return ResponseEntity.ok(dashboardService.getProTagDistribution(userId));
        }
        return ResponseEntity.ok(dashboardService.getStaffTagDistribution());
    }
}
