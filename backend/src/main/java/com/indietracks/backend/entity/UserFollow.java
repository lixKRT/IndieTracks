package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("user_follows")
public class UserFollow {
    private Integer user_id;
    private Integer followed_user_id;
    private LocalDateTime created_at;
}
