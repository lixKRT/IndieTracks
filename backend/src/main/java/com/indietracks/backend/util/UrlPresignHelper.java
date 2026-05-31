package com.indietracks.backend.util;

import com.indietracks.backend.dto.*;
import com.indietracks.backend.service.MinioService;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * URL 预签名统一工具 — 消灭 7 个 service 中散落的 minioService.getPresignedUrl() 调用
 *
 * 用法:
 *   urlPresignHelper.presignAlbumList(albums);
 *   urlPresignHelper.presignCircleList(circles);
 *   urlPresignHelper.presignDetail(detail);
 */
@Component
public class UrlPresignHelper {

    private final MinioService minioService;

    public UrlPresignHelper(MinioService minioService) {
        this.minioService = minioService;
    }

    // ===== 专辑 =====

    public void presignAlbumList(List<AlbumListItem> items) {
        if (items == null) return;
        items.forEach(this::presignAlbumListItem);
    }

    public void presignAlbumListItem(AlbumListItem item) {
        if (item == null) return;
        item.setCover_url(url(item.getCover_url()));
        item.setCircle_logo_url(url(item.getCircle_logo_url()));
    }

    public void presignAlbumDetail(AlbumDetail detail) {
        if (detail == null) return;
        detail.setCover_url(url(detail.getCover_url()));
        if (detail.getCircle() != null) {
            detail.getCircle().setLogo_url(url(detail.getCircle().getLogo_url()));
        }
        if (detail.getTracks() != null) {
            // tracks 的 preview_url 由调用方构造 objectKey 后传入
        }
        presignComments(detail.getComments());
    }

    public void presignTracks(List<AlbumDetail.TrackInfo> tracks) {
        if (tracks == null) return;
        tracks.forEach(t -> t.setPreview_url(url(t.getPreview_url())));
    }

    // ===== 社团 =====

    public void presignCircleList(List<CircleListItem> items) {
        if (items == null) return;
        items.forEach(c -> c.setLogo_url(url(c.getLogo_url())));
    }

    public void presignCircleListItem(CircleListItem item) {
        if (item == null) return;
        item.setLogo_url(url(item.getLogo_url()));
    }

    public void presignCircleDetail(CircleDetail detail) {
        if (detail == null) return;
        detail.setLogo_url(url(detail.getLogo_url()));
        if (detail.getAlbums() != null) {
            presignAlbumList(detail.getAlbums());
        }
        if (detail.getMembers() != null) {
            detail.getMembers().forEach(m -> m.setAvatar_url(url(m.getAvatar_url())));
        }
    }

    public void presignPreviewAlbums(List<CircleListItem.PreviewAlbum> items) {
        if (items == null) return;
        items.forEach(p -> p.setCover_url(url(p.getCover_url())));
    }

    // ===== 用户 =====

    public void presignUserDTO(UserDTO dto) {
        if (dto == null) return;
        dto.setAvatar_url(url(dto.getAvatar_url()));
    }

    public void presignUserDTOList(List<UserDTO> list) {
        if (list == null) return;
        list.forEach(this::presignUserDTO);
    }

    // ===== 评论 =====

    public void presignComments(List<AlbumDetail.CommentInfo> comments) {
        if (comments == null) return;
        comments.forEach(c -> c.setAvatar_url(url(c.getAvatar_url())));
    }

    // ===== 内部 =====

    private String url(String objectKey) {
        return minioService.getPresignedUrl(objectKey);
    }
}
