package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/** 用户关注关系实体，联合主键 (user_id, followed_user_id) */
@Data
@TableName("user_follows")
public class UserFollow {
    private Integer user_id;            // 关注者 ID，联合主键之一，关联 users 表，ON DELETE CASCADE
    private Integer followed_user_id;   // 被关注者 ID，联合主键之一，关联 users 表，ON DELETE CASCADE
    private LocalDateTime created_at;   // 关注时间，数据库自动生成
}
