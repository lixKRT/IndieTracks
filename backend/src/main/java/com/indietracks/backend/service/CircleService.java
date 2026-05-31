package com.indietracks.backend.service;

import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.dto.CircleDetail;
import com.indietracks.backend.dto.CircleListItem;
import com.indietracks.backend.entity.Circle;
import com.indietracks.backend.mapper.AlbumMapper;
import com.indietracks.backend.mapper.CircleMapper;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class CircleService {

    private final CircleMapper circleMapper;
    private final AlbumMapper albumMapper;
    private final MinioService minioService;

    public CircleService(CircleMapper circleMapper, AlbumMapper albumMapper, MinioService minioService) {
        this.circleMapper = circleMapper;
        this.albumMapper = albumMapper;
        this.minioService = minioService;
    }

    public List<CircleListItem> getCircleList() {
        List<CircleListItem> circles = circleMapper.selectCircleList();
        if (circles.isEmpty()) {
            return circles;
        }

        // 批量获取所有社团的专辑，计算 representative_tags 和 preview_albums
        List<Integer> circleIds = circles.stream()
                .map(CircleListItem::getCircle_id)
                .toList();
        List<AlbumListItem> allAlbums = albumMapper.selectAlbumsByCircleIds(circleIds);

        Map<Integer, List<AlbumListItem>> albumsByCircle = allAlbums.stream()
                .collect(Collectors.groupingBy(AlbumListItem::getCircle_id));

        for (CircleListItem circle : circles) {
            // 社团 logo URL 转换
            circle.setLogo_url(minioService.getPresignedUrl(circle.getLogo_url()));

            List<AlbumListItem> circleAlbums = albumsByCircle.getOrDefault(circle.getCircle_id(), Collections.emptyList());

            // representative_tags: 统计标签频率取前3
            Map<String, Integer> tagFreq = new HashMap<>();
            for (AlbumListItem album : circleAlbums) {
                if (album.getTags() != null) {
                    for (String tag : album.getTags()) {
                        tagFreq.merge(tag, 1, Integer::sum);
                    }
                }
            }
            List<String> representativeTags = tagFreq.entrySet().stream()
                    .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
                    .limit(3)
                    .map(Map.Entry::getKey)
                    .toList();
            circle.setRepresentative_tags(representativeTags);

            // preview_albums: 最新4张专辑
            List<AlbumListItem> sorted = circleAlbums.stream()
                    .sorted((a, b) -> {
                        if (a.getPublish_date() == null) return 1;
                        if (b.getPublish_date() == null) return -1;
                        return b.getPublish_date().compareTo(a.getPublish_date());
                    })
                    .toList();
            List<CircleListItem.PreviewAlbum> previewAlbums = sorted.stream()
                    .limit(4)
                    .map(a -> {
                        CircleListItem.PreviewAlbum pa = new CircleListItem.PreviewAlbum();
                        pa.setAlbum_id(a.getAlbum_id());
                        pa.setTitle(a.getTitle());
                        pa.setCover_url(minioService.getPresignedUrl(a.getCover_url()));
                        pa.setTags(a.getTags() != null ? a.getTags().subList(0, Math.min(2, a.getTags().size())) : Collections.emptyList());
                        return pa;
                    })
                    .toList();
            circle.setPreview_albums(previewAlbums);
        }

        return circles;
    }

    public CircleDetail getCircleDetail(Integer circleId) {
        Circle circle = circleMapper.selectById(circleId);
        if (circle == null) {
            return null;
        }

        CircleDetail detail = new CircleDetail();
        detail.setCircle_id(circle.getCircle_id());
        detail.setName(circle.getName());
        detail.setLogo_url(minioService.getPresignedUrl(circle.getLogo_url()));
        detail.setDescription(circle.getDescription());

        // 该社团的专辑（转换封面 URL）
        List<AlbumListItem> albums = albumMapper.selectAlbumsByCircleId(circleId);
        albums.forEach(a -> {
            a.setCover_url(minioService.getPresignedUrl(a.getCover_url()));
            a.setCircle_logo_url(minioService.getPresignedUrl(a.getCircle_logo_url()));
        });
        detail.setAlbums(albums);

        // representative_tags: 统计标签频率取前3
        Map<String, Integer> tagFreq = new HashMap<>();
        for (AlbumListItem album : albums) {
            if (album.getTags() != null) {
                for (String tag : album.getTags()) {
                    tagFreq.merge(tag, 1, Integer::sum);
                }
            }
        }
        List<String> representativeTags = tagFreq.entrySet().stream()
                .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
                .limit(3)
                .map(Map.Entry::getKey)
                .toList();
        detail.setRepresentative_tags(representativeTags);

        // 成员（转换头像 URL）
        List<CircleDetail.CircleMember> members = circleMapper.selectMembersByCircleId(circleId);
        members.forEach(m -> m.setAvatar_url(minioService.getPresignedUrl(m.getAvatar_url())));
        detail.setMembers(members);

        return detail;
    }
}
