package com.indietracks.backend.dto;

import lombok.Data;

import java.util.List;

/**
 * 社团详情 DTO — 包含代表标签、专辑列表和成员信息。
 * <p>用于 {@code /api/label/{id}} 接口返回，前端社团详情页直接消费。</p>
 */
@Data
public class CircleDetail {

    /** 社团主键 ID */
    private Integer circle_id;

    /** 社团名称 */
    private String name;

    /** 社团 Logo URL（MinIO 对象 Key） */
    private String logo_url;

    /** 社团简介/描述 */
    private String description;

    /**
     * 社团代表标签列表。
     * <p>取与社团关联专辑中出现频次最高的标签名称，用于社团卡片展示。</p>
     */
    private List<String> representative_tags;

    /** 社团下的专辑列表，使用 {@link AlbumListItem} 精简信息 */
    private List<AlbumListItem> albums;

    /** 社团成员列表 */
    private List<CircleMember> members;

    /**
     * 社团成员简要信息。
     * <p>仅包含基础用户信息，用于社团详情页成员展示。</p>
     */
    @Data
    public static class CircleMember {

        /** 成员用户主键 ID */
        private Integer user_id;

        /** 成员用户名 */
        private String username;

        /** 成员头像 URL（MinIO 对象 Key） */
        private String avatar_url;

        /**
         * 用户角色。
         * <p>可选值：</p>
         * <ul>
         *   <li>{@code normal} — 普通用户</li>
         *   <li>{@code pro} — 专业用户</li>
         *   <li>{@code staff} — 工作人员</li>
         * </ul>
         */
        private String user_role;
    }
}
