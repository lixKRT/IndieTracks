package com.indietracks.backend.dto;

import lombok.Data;

import java.util.List;

/**
 * 统一分页响应 DTO — 消灭 Controller 中重复的 HashMap 构造。
 * <p>泛型参数 {@code T} 为列表项的具体 DTO 类型，
 * 如 {@link AlbumListItem}、{@link CircleListItem} 等。</p>
 *
 * @param <T> 分页数据列表中每个元素的类型
 */
@Data
public class PagedResponse<T> {

    /** 当前页数据列表 */
    private List<T> data;

    /** 符合条件的总记录数 */
    private long total;

    /** 当前页码（从 1 开始） */
    private long page;

    /** 每页大小 */
    private long page_size;

    /**
     * 全参构造方法。
     *
     * @param data     当前页数据列表
     * @param total    符合条件的总记录数
     * @param page     当前页码（从 1 开始）
     * @param pageSize 每页大小
     */
    public PagedResponse(List<T> data, long total, long page, long pageSize) {
        this.data = data;
        this.total = total;
        this.page = page;
        this.page_size = pageSize;
    }

    /**
     * 静态工厂方法 — 简化分页响应的构造。
     * <p>用法示例：</p>
     * <pre>{@code
     * return PagedResponse.of(albums, total, page, size);
     * }</pre>
     *
     * @param data     当前页数据列表
     * @param total    符合条件的总记录数
     * @param page     当前页码（从 1 开始）
     * @param pageSize 每页大小
     * @param <T>      列表元素类型
     * @return 新构造的分页响应实例
     */
    public static <T> PagedResponse<T> of(List<T> data, long total, long page, long pageSize) {
        return new PagedResponse<>(data, total, page, pageSize);
    }
}
