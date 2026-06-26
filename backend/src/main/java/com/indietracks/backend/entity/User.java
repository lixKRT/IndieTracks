package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/** 用户实体，支持 dizzylab 关联与角色分级 */
@Data
@TableName("users")
public class User {
    @TableId(type = IdType.AUTO)
    private Integer user_id;
    private Integer dizzylab_user_id;       // dizzylab 平台用户 ID，UNIQUE，可为 null
    private String username;                // 用户名，UNIQUE NOT NULL
    private String email;                   // 邮箱，UNIQUE，可为 null
    private String password_hash;           // BCrypt 加密后的密码，可为 null
    private String avatar_url;              // MinIO 对象 Key，前端拼接完整地址，可为 null
    private String user_role;               // 角色：normal / pro / staff，默认 normal
    private LocalDateTime created_at;       // 注册时间，数据库自动生成
    private LocalDateTime userpage_crawled_at; // 爬虫最近抓取时间，可为 null
}
