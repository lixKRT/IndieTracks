package com.indietracks.backend.dto;

import lombok.Data;

/**
 * 统一错误响应 DTO
 */
@Data
public class ErrorResponse {
    private String error;   // 错误描述信息
    private int status;     // HTTP 状态码，如 400、401、404、500

    public ErrorResponse(String error, int status) {
        this.error = error;
        this.status = status;
    }

    public static ErrorResponse of(String error, int status) {
        return new ErrorResponse(error, status);
    }
}
