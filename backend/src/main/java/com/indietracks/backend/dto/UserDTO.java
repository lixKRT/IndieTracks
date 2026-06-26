package com.indietracks.backend.dto;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户信息 DTO — 用于前端展示。
 * <p>包含用户基本信息及其所属社团名称，
 * 用于用户主页、评论区头像旁展示等场景。</p>
 */
@Data
public class UserDTO {

    /** 用户主键 ID */
    private Integer user_id;

    /** 用户名 */
    private String username;

    /** 用户头像 URL（MinIO 对象 Key） */
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

    /**
     * 所属社团名称。
     * <p>可为 {@code null}，表示用户未加入任何社团。</p>
     */
    private String circle_name;
}
