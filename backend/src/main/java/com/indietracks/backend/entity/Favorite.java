package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/** 收藏关联表，联合主键（user_id + album_id），无自增主键 */
@Data
@TableName("favorites")
public class Favorite {
    private Integer user_id;
    private Integer album_id;
    private LocalDateTime created_at;
}
