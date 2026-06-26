package com.indietracks.backend.dto;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 专辑详情 DTO — 包含社团、标签、曲目、评论等完整信息。
 * <p>用于 {@code /api/album/{id}} 接口返回，前端专辑详情页直接消费。</p>
 */
@Data
public class AlbumDetail {

    /** 专辑主键 ID */
    private Integer album_id;

    /** 专辑标题 */
    private String title;

    /**
     * 专辑所属社团简要信息。
     * <p>可为 {@code null}，表示无社团归属的独立专辑。</p>
     */
    private AlbumCircleInfo circle;

    /** 封面图 URL（MinIO 对象 Key） */
    private String cover_url;

    /**
     * 专辑价格。
     * <p>使用 {@link BigDecimal} 避免浮点精度丢失。</p>
     */
    private BigDecimal price;

    /** 发布日期 */
    private LocalDateTime publish_date;

    /** 专辑介绍标题（替代原 description 字段） */
    private String info_title;

    /** 专辑介绍正文，支持富文本内容 */
    private String info_content;

    /** 专辑关联标签列表 */
    private List<TagInfo> tags;

    /** 专辑曲目列表 */
    private List<TrackInfo> tracks;

    /**
     * 专辑评论列表。
     * <p>返回完整列表而非单条，前端直接渲染。</p>
     */
    private List<CommentInfo> comments;

    /**
     * 专辑所属社团简要信息。
     * <p>仅包含 ID、名称和 Logo，用于专辑详情页头部展示。</p>
     */
    @Data
    public static class AlbumCircleInfo {

        /** 社团主键 ID */
        private Integer circle_id;

        /** 社团名称 */
        private String name;

        /** 社团 Logo URL（MinIO 对象 Key） */
        private String logo_url;
    }

    /**
     * 专辑关联标签。
     * <p>对应数据库 {@code album_tags} 中间表关联的标签记录。</p>
     */
    @Data
    public static class TagInfo {

        /** 标签主键 ID */
        private Integer tag_id;

        /** 标签名称 */
        private String name;
    }

    /**
     * 曲目信息 — 对应数据库 {@code work_files} 表。
     * <p>每条记录代表专辑中的一首曲目，含试听和完整音频两种类型。</p>
     */
    @Data
    public static class TrackInfo {

        /** 文件主键 ID */
        private Integer file_id;

        /** 文件名称（曲目名） */
        private String file_name;

        /** 曲目时长，格式为 {@code "mm:ss"} */
        private String track_length;

        /** 排序序号，数值越小越靠前 */
        private Integer sort_order;

        /**
         * 文件类型。
         * <p>可选值：</p>
         * <ul>
         *   <li>{@code preview} — 试听片段</li>
         *   <li>{@code full} — 完整音频</li>
         * </ul>
         */
        private String file_type;

        /**
         * 音频文件预览地址（MinIO 对象 Key）。
         * <p>前端需拼接 MinIO 代理前缀生成完整可访问 URL。</p>
         */
        private String preview_url;
    }

    /**
     * 评论信息 — 含评论者基础用户信息。
     * <p>对应数据库 {@code comments} 表，关联 {@code users} 表获取用户信息。</p>
     */
    @Data
    public static class CommentInfo {

        /** 评论主键 ID */
        private Integer comment_id;

        /**
         * 评论者用户 ID。
         * <p>可为 {@code null}，当用户注销后数据库 SET NULL。</p>
         */
        private Integer user_id;

        /** 评论者用户名 */
        private String username;

        /** 评论者头像 URL（MinIO 对象 Key） */
        private String avatar_url;

        /** 评论正文内容 */
        private String content;

        /** 评论创建时间 */
        private LocalDateTime created_at;
    }
}
