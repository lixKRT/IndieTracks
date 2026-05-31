package com.indietracks.backend.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.indietracks.backend.dto.AlbumDetail;
import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.entity.Album;
import com.indietracks.backend.mapper.AlbumMapper;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class AlbumService {

    private final AlbumMapper albumMapper;
    private final MinioService minioService;

    public AlbumService(AlbumMapper albumMapper, MinioService minioService) {
        this.albumMapper = albumMapper;
        this.minioService = minioService;
    }

    public IPage<AlbumListItem> getAlbumList(int page, int pageSize, String tag, String search, String price, String sort) {
        Page<AlbumListItem> pageParam = new Page<>(page, pageSize);
        IPage<AlbumListItem> result = albumMapper.selectAlbumList(pageParam, tag, search, price, sort);
        result.getRecords().forEach(this::convertAlbumListUrls);
        return result;
    }

    public AlbumDetail getAlbumDetail(Integer albumId) {
        Album album = albumMapper.selectById(albumId);
        if (album == null) {
            return null;
        }

        AlbumDetail detail = new AlbumDetail();
        detail.setAlbum_id(album.getAlbum_id());
        detail.setTitle(album.getTitle());
        detail.setCover_url(minioService.getPresignedUrl(album.getCover_url()));
        detail.setPrice(album.getPrice());
        detail.setPublish_date(album.getPublish_date());
        detail.setInfo_title(album.getInfo_title());
        detail.setInfo_content(album.getInfo_content());

        // 社团信息
        AlbumDetail.AlbumCircleInfo circle = albumMapper.selectCircleByAlbumId(albumId);
        if (circle != null) {
            circle.setLogo_url(minioService.getPresignedUrl(circle.getLogo_url()));
        }
        detail.setCircle(circle);

        // 标签
        detail.setTags(albumMapper.selectTagsByAlbumId(albumId));

        // 曲目 + 预签名 URL
        List<AlbumDetail.TrackInfo> tracks = albumMapper.selectTracksByAlbumId(albumId);
        for (AlbumDetail.TrackInfo track : tracks) {
            track.setPreview_url(minioService.getPresignedUrl(getObjectKeyFromTrack(track, album)));
        }
        detail.setTracks(tracks);

        // 评论（首页 5 条，头像 URL 转换）
        List<AlbumDetail.CommentInfo> comments = albumMapper.selectCommentsPage(albumId, 5, 0);
        comments.forEach(c -> c.setAvatar_url(minioService.getPresignedUrl(c.getAvatar_url())));
        detail.setComments(comments);

        return detail;
    }

    public Map<String, Object> getComments(Integer albumId, int page, int pageSize) {
        int total = albumMapper.countCommentsByAlbumId(albumId);
        int offset = (page - 1) * pageSize;
        List<AlbumDetail.CommentInfo> comments = albumMapper.selectCommentsPage(albumId, pageSize, offset);
        comments.forEach(c -> c.setAvatar_url(minioService.getPresignedUrl(c.getAvatar_url())));

        Map<String, Object> result = new HashMap<>();
        result.put("data", comments);
        result.put("total", total);
        result.put("page", page);
        result.put("page_size", pageSize);
        return result;
    }

    private void convertAlbumListUrls(AlbumListItem item) {
        item.setCover_url(minioService.getPresignedUrl(item.getCover_url()));
        item.setCircle_logo_url(minioService.getPresignedUrl(item.getCircle_logo_url()));
    }

    private String getObjectKeyFromTrack(AlbumDetail.TrackInfo track, Album album) {
        if (track.getFile_type() == null) return null;
        String prefix = "preview".equals(track.getFile_type()) ? "audio/preview/" : "audio/full/";
        String slug = album.getDizzylab_id();
        String filename = String.format("%03d.mp3", track.getSort_order());
        return prefix + slug + "/" + filename;
    }
}
