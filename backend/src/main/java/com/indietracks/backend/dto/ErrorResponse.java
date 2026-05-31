package com.indietracks.backend.dto;

import lombok.Data;

/**
 * 统一错误响应 DTO
 */
@Data
public class ErrorResponse {
    private String error;
    private int status;

    public ErrorResponse(String error, int status) {
        this.error = error;
        this.status = status;
    }

    public static ErrorResponse of(String error, int status) {
        return new ErrorResponse(error, status);
    }
}
