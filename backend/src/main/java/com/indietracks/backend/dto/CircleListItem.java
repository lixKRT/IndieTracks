package com.indietracks.backend.dto;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 社团列表项 DTO — 展示社团卡片所需的精简信息。
 * <p>用于社团列表页以卡片形式展示社团概要，
 * 相比 {@link CircleDetail} 省略了完整成员列表以提升查询性能。</p>
 */
@Data
public class CircleListItem {

    /** 社团主键 ID */
    private Integer circle_id;

    /** 社团名称 */
    private String name;

    /** 社团 Logo URL（MinIO 对象 Key） */
    private String logo_url;

    /** 社团简介/描述 */
    private String description;

    /** 社团下专辑总数 */
    private Integer album_count;

    /** 社团成员总数 */
    private Integer member_count;

    /** 最新一张专辑的发布日期，用于排序和展示活跃度 */
    private LocalDateTime latest_album_date;

    /**
     * 社团代表标签列表。
     * <p>取与社团关联专辑中出现频次最高的标签名称，用于社团卡片展示。</p>
     */
    private List<String> representative_tags;

    /**
     * 预览专辑列表。
     * <p>仅用于社团卡片展示，包含少量精简专辑信息。</p>
     */
    private List<PreviewAlbum> preview_albums;

    /**
     * 社团卡片预览专辑。
     * <p>仅包含最基础的展示字段，用于社团列表卡片的缩略图轮播。</p>
     */
    @Data
    public static class PreviewAlbum {

        /** 专辑主键 ID */
        private Integer album_id;

        /** 专辑标题 */
        private String title;

        /** 封面图 URL（MinIO 对象 Key） */
        private String cover_url;

        /** 专辑关联标签名称列表 */
        private List<String> tags;
    }
}
