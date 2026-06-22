package com.indietracks.backend.service.admin;

import com.indietracks.backend.mapper.*;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class AdminDashboardService {

    private final UserMapper userMapper;
    private final AlbumMapper albumMapper;
    private final CircleMapper circleMapper;
    private final CommentMapper commentMapper;
    private final FavoriteMapper favoriteMapper;
    private final TagMapper tagMapper;

    public AdminDashboardService(UserMapper userMapper, AlbumMapper albumMapper,
                                  CircleMapper circleMapper, CommentMapper commentMapper,
                                  FavoriteMapper favoriteMapper, TagMapper tagMapper) {
        this.userMapper = userMapper;
        this.albumMapper = albumMapper;
        this.circleMapper = circleMapper;
        this.commentMapper = commentMapper;
        this.favoriteMapper = favoriteMapper;
        this.tagMapper = tagMapper;
    }

    // ===== Staff 统计 =====

    public Map<String, Object> getStaffStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalUsers", userMapper.selectCount(null));
        stats.put("totalAlbums", albumMapper.selectCount(null));
        stats.put("totalCircles", circleMapper.selectCircleCount());
        stats.put("totalComments", commentMapper.selectCount(null));
        stats.put("totalFavorites", favoriteMapper.selectCount(null));
        return stats;
    }

    public Map<String, Object> getStaffTrends(String period) {
        Map<String, Object> trends = new HashMap<>();
        // TODO: 实现趋势数据查询
        trends.put("userTrends", Collections.emptyList());
        trends.put("albumTrends", Collections.emptyList());
        return trends;
    }

    public List<Map<String, Object>> getStaffTopAlbums(String period, int limit) {
        // TODO: 实现热门专辑排行
        return Collections.emptyList();
    }

    public List<Map<String, Object>> getStaffTopCircles(String period, int limit) {
        // TODO: 实现活跃社团排行
        return Collections.emptyList();
    }

    public List<Map<String, Object>> getStaffTagDistribution() {
        // TODO: 实现标签分布
        return Collections.emptyList();
    }

    // ===== Pro 统计（仅所属社团） =====

    public Map<String, Object> getProStats(Integer userId) {
        Map<String, Object> stats = new HashMap<>();
        // TODO: 查询用户所属社团的专辑数
        stats.put("totalAlbums", 0);
        stats.put("totalComments", 0);
        stats.put("totalFavorites", 0);
        return stats;
    }

    public Map<String, Object> getProTrends(Integer userId, String period) {
        Map<String, Object> trends = new HashMap<>();
        // TODO: 实现所属社团趋势数据
        trends.put("albumTrends", Collections.emptyList());
        return trends;
    }

    public List<Map<String, Object>> getProTopAlbums(Integer userId, String period, int limit) {
        // TODO: 实现所属社团热门专辑
        return Collections.emptyList();
    }

    public List<Map<String, Object>> getProTopCircles(Integer userId, String period, int limit) {
        // Pro 用户不显示社团排行
        return Collections.emptyList();
    }

    public List<Map<String, Object>> getProTagDistribution(Integer userId) {
        // TODO: 实现所属社团标签分布
        return Collections.emptyList();
    }
}
