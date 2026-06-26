package com.indietracks.backend.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/** 登录请求 DTO */
@Data
public class LoginRequest {
    @NotBlank(message = "用户名或邮箱不能为空")
    private String account;              // 支持用户名或邮箱登录

    @NotBlank(message = "密码不能为空")
    private String password;

    private boolean remember_me;         // true 时延长 JWT 过期时间
}
