package com.indietracks.backend.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class LoginRequest {
    @NotBlank(message = "用户名或邮箱不能为空")
    private String account;

    @NotBlank(message = "密码不能为空")
    private String password;

    private boolean remember_me;
}
