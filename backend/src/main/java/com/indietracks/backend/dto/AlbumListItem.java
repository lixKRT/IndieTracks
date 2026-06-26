package com.indietracks.backend.dto;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 专辑列表项 DTO — 展示专辑卡片所需的精简信息。
 * <p>用于首页、社团详情页、标签页等需要以卡片形式展示专辑列表的场景。
 * 相比 {@link AlbumDetail}，省略了曲目、评论等重量级字段以提升列表查询性能。</p>
 */
@Data
public class AlbumListItem {

    /** 专辑主键 ID */
    private Integer album_id;

    /** 专辑标题 */
    private String title;

    /** 所属社团主键 ID，可为 {@code null}（独立专辑） */
    private Integer circle_id;

    /** 所属社团名称，可为 {@code null} */
    private String circle_name;

    /** 所属社团 Logo URL（MinIO 对象 Key），可为 {@code null} */
    private String circle_logo_url;

    /** 封面图 URL（MinIO 对象 Key） */
    private String cover_url;

    /** 专辑介绍标题（替代原 description 字段） */
    private String info_title;

    /** 专辑介绍正文 */
    private String info_content;

    /**
     * 专辑价格。
     * <p>使用 {@link BigDecimal} 避免浮点精度丢失。</p>
     */
    private BigDecimal price;

    /** 发布日期 */
    private LocalDateTime publish_date;

    /**
     * 标签名列表。
     * <p>仅包含标签名称字符串，非完整 {@link AlbumDetail.TagInfo} 对象，
     * 用于卡片上快速展示标签。</p>
     */
    private List<String> tags;

    /** 专辑曲目总数 */
    private Integer track_count;
}
