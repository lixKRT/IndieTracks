package com.indietracks.backend.service;

import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.dto.CircleListItem;
import com.indietracks.backend.mapper.AlbumMapper;
import com.indietracks.backend.mapper.CircleFollowMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

/** 社团关注服务 — 关注/取关、查询已关注社团列表 */
@Service
public class CircleFollowService {

    private final CircleFollowMapper circleFollowMapper;
    private final AlbumMapper albumMapper;
    private final UrlPresignHelper urlPresign;

    public CircleFollowService(CircleFollowMapper circleFollowMapper,
                               AlbumMapper albumMapper, UrlPresignHelper urlPresign) {
        this.circleFollowMapper = circleFollowMapper;
        this.albumMapper = albumMapper;
        this.urlPresign = urlPresign;
    }

    public void follow(Integer userId, Integer circleId) {
        circleFollowMapper.insertFollow(userId, circleId);
    }

    public void unfollow(Integer userId, Integer circleId) {
        circleFollowMapper.deleteFollow(userId, circleId);
    }

    public boolean isFollowing(Integer userId, Integer circleId) {
        return circleFollowMapper.countFollow(userId, circleId) > 0;
    }

    /** 返回列表中每个社团附带代表性标签和最新专辑预览 */
    public List<CircleListItem> getFollowedCircles(Integer userId) {
        List<CircleListItem> circles = circleFollowMapper.selectFollowedCircles(userId);
        if (circles.isEmpty()) return circles;

        // 批量加载所有关注社团的专辑
        List<Integer> circleIds = circles.stream().map(CircleListItem::getCircle_id).toList();
        List<AlbumListItem> allAlbums = albumMapper.selectAlbumsByCircleIds(circleIds);
        Map<Integer, List<AlbumListItem>> albumsByCircle = allAlbums.stream()
                .collect(Collectors.groupingBy(AlbumListItem::getCircle_id));

        for (CircleListItem circle : circles) {
            List<AlbumListItem> circleAlbums = albumsByCircle.getOrDefault(circle.getCircle_id(), Collections.emptyList());
            circle.setRepresentative_tags(extractTopTags(circleAlbums, 3));
            circle.setPreview_albums(buildPreviewAlbums(circleAlbums, 4));
        }

        // 统一预签名
        urlPresign.presignCircleList(circles);
        for (CircleListItem circle : circles) {
            urlPresign.presignPreviewAlbums(circle.getPreview_albums());
        }

        return circles;
    }

    /** 按出现频率降序取前 N 个标签 */
    private List<String> extractTopTags(List<AlbumListItem> albums, int limit) {
        Map<String, Integer> tagFreq = new HashMap<>();
        for (AlbumListItem album : albums) {
            if (album.getTags() != null) {
                for (String tag : album.getTags()) {
                    tagFreq.merge(tag, 1, Integer::sum);
                }
            }
        }
        return tagFreq.entrySet().stream()
                .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
                .limit(limit)
                .map(Map.Entry::getKey)
                .toList();
    }

    /** 按发布日期降序取前 limit 个专辑，每张最多保留 2 个标签，null 日期排末尾 */
    private List<CircleListItem.PreviewAlbum> buildPreviewAlbums(List<AlbumListItem> albums, int limit) {
        return albums.stream()
                .sorted((a, b) -> {
                    if (a.getPublish_date() == null) return 1;
                    if (b.getPublish_date() == null) return -1;
                    return b.getPublish_date().compareTo(a.getPublish_date());
                })
                .limit(limit)
                .map(a -> {
                    CircleListItem.PreviewAlbum pa = new CircleListItem.PreviewAlbum();
                    pa.setAlbum_id(a.getAlbum_id());
                    pa.setTitle(a.getTitle());
                    pa.setCover_url(a.getCover_url());
                    pa.setTags(a.getTags() != null ? a.getTags().subList(0, Math.min(2, a.getTags().size())) : Collections.emptyList());
                    return pa;
                })
                .toList();
    }
}
