package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 用户关注社团关联表，对应 circle_follows 表。
 * <p>联合主键（user_id + circle_id），无自增主键。
 * 任一端删除时 CASCADE 级联删除。</p>
 */
@Data
@TableName("circle_follows")
public class CircleFollow {
    /** 用户 ID，关联 users 表，用户删除后 CASCADE */
    private Integer user_id;

    /** 社团 ID，关联 circles 表，社团删除后 CASCADE */
    private Integer circle_id;

    /** 关注时间 */
    private LocalDateTime created_at;
}
