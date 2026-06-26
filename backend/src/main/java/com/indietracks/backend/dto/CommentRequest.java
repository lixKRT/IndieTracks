package com.indietracks.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

/** 评论提交请求 DTO */
@Data
public class CommentRequest {
    @NotBlank(message = "评论内容不能为空")
    @Size(max = 1000, message = "评论长度不能超过 1000 字符")
    private String content;
}
