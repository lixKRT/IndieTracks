package com.indietracks.backend.dto;

import lombok.Data;

import java.util.List;

/**
 * 统一分页响应 DTO — 消灭 Controller 中重复的 HashMap 构造
 */
@Data
public class PagedResponse<T> {
    private List<T> data;
    private long total;
    private long page;
    private long page_size;

    public PagedResponse(List<T> data, long total, long page, long pageSize) {
        this.data = data;
        this.total = total;
        this.page = page;
        this.page_size = pageSize;
    }

    public static <T> PagedResponse<T> of(List<T> data, long total, long page, long pageSize) {
        return new PagedResponse<>(data, total, page, pageSize);
    }
}
