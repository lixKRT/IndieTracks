package com.indietracks.backend.service;

import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.dto.CircleDetail;
import com.indietracks.backend.dto.CircleListItem;
import com.indietracks.backend.entity.Circle;
import com.indietracks.backend.mapper.AlbumMapper;
import com.indietracks.backend.mapper.CircleMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class CircleService {

    private final CircleMapper circleMapper;
    private final AlbumMapper albumMapper;
    private final UrlPresignHelper urlPresign;

    public CircleService(CircleMapper circleMapper, AlbumMapper albumMapper, UrlPresignHelper urlPresign) {
        this.circleMapper = circleMapper;
        this.albumMapper = albumMapper;
        this.urlPresign = urlPresign;
    }

    public List<CircleListItem> getCircleList() {
        List<CircleListItem> circles = circleMapper.selectCircleList();
        if (circles.isEmpty()) return circles;

        enrichCircles(circles);
        return circles;
    }

    public Map<String, Object> getCircleListPaged(int page, int pageSize) {
        int offset = (page - 1) * pageSize;
        List<CircleListItem> circles = circleMapper.selectCircleListPaged(offset, pageSize);
        int total = circleMapper.selectCircleCount();

        if (!circles.isEmpty()) {
            enrichCircles(circles);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("data", circles);
        result.put("total", total);
        result.put("page", page);
        result.put("page_size", pageSize);
        return result;
    }

    private void enrichCircles(List<CircleListItem> circles) {
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
    }

    public CircleDetail getCircleDetail(Integer circleId) {
        Circle circle = circleMapper.selectById(circleId);
        if (circle == null) return null;

        CircleDetail detail = new CircleDetail();
        detail.setCircle_id(circle.getCircle_id());
        detail.setName(circle.getName());
        detail.setLogo_url(circle.getLogo_url());
        detail.setDescription(circle.getDescription());

        List<AlbumListItem> albums = albumMapper.selectAlbumsByCircleId(circleId);
        detail.setAlbums(albums);
        detail.setRepresentative_tags(extractTopTags(albums, 3));

        List<CircleDetail.CircleMember> members = circleMapper.selectMembersByCircleId(circleId);
        detail.setMembers(members);

        // 统一预签名
        urlPresign.presignCircleDetail(detail);

        return detail;
    }

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
