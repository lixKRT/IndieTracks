package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/** 评论实体，同一用户对同一专辑同内容有唯一约束 */
@Data
@TableName("comments")
public class Comment {
    @TableId(type = IdType.AUTO)
    private Integer comment_id;
    private Integer user_id;       // 用户删除后 SET NULL，可为 null
    private Integer album_id;      // 专辑删除后 CASCADE
    private String content;
    private LocalDateTime created_at;
}
