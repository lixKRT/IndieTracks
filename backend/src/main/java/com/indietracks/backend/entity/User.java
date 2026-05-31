package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("users")
public class User {
    @TableId(type = IdType.AUTO)
    private Integer user_id;
    private Integer dizzylab_user_id;
    private String username;
    private String email;
    private String password_hash;
    private String avatar_url;
    private String user_role;
    private LocalDateTime created_at;
    private LocalDateTime userpage_crawled_at;
}
