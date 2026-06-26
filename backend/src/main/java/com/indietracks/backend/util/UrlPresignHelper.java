package com.indietracks.backend.util;

import com.indietracks.backend.dto.*;
import com.indietracks.backend.service.MinioService;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * URL 预签名统一工具 — 集中处理 DTO 中的 MinIO objectKey → 临时签名 URL 转换。
 * 将各 service 中散落的 minioService.getPresignedUrl() 调用收拢到一处，避免重复代码。
 *
 * 用法:
 *   urlPresignHelper.presignAlbumList(albums);
 *   urlPresignHelper.presignCircleList(circles);
 *   urlPresignHelper.presignDetail(detail);
 *
 * <p>所有字段传入时应为 MinIO objectKey（如 "cover/abc.jpg"），
 * 调用后原地替换为带签名的临时访问 URL。</p>
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

    /** 预签名专辑详情 — 含封面、社团 logo、评论头像；嵌套对象逐层处理 */
    public void presignAlbumDetail(AlbumDetail detail) {
        if (detail == null) return;
        detail.setCover_url(url(detail.getCover_url()));
        if (detail.getCircle() != null) {
            detail.getCircle().setLogo_url(url(detail.getCircle().getLogo_url()));
        }
        if (detail.getTracks() != null) {
            // tracks 的 preview_url 由调用方构造 objectKey 后传入，此处不处理
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

    /** 预签名社团详情 — 含 logo、关联专辑列表、成员头像 */
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

    /** objectKey → 带签名的临时访问 URL（可为 null，MinIO 层会处理） */
    private String url(String objectKey) {
        return minioService.getPresignedUrl(objectKey);
    }
}
