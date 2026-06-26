package com.indietracks.backend.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 注册请求 DTO。
 * <p>用于 {@code POST /api/auth/register} 接口，
 * 所有字段均通过 {@code jakarta.validation} 注解进行参数校验。</p>
 */
@Data
public class RegisterRequest {

    /**
     * 用户名。
     * <p>不能为空，长度限制 2-20 个字符。</p>
     */
    @NotBlank(message = "用户名不能为空")
    @Size(min = 2, max = 20, message = "用户名长度 2-20 字符")
    private String username;

    /**
     * 邮箱地址。
     * <p>不能为空，必须符合标准邮箱格式。</p>
     */
    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;

    /**
     * 密码（明文）。
     * <p>不能为空，长度限制 6-100 个字符。
     * 后端接收后使用 BCrypt 加密存储。</p>
     */
    @NotBlank(message = "密码不能为空")
    @Size(min = 6, max = 100, message = "密码长度 6-100 字符")
    private String password;
}
