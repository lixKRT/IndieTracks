package com.indietracks.backend.service;

import com.indietracks.backend.entity.Tag;
import com.indietracks.backend.mapper.TagMapper;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 标签服务 — 获取热门标签
 */
@Service
public class TagService {

    private final TagMapper tagMapper;

    public TagService(TagMapper tagMapper) {
        this.tagMapper = tagMapper;
    }

    /**
     * 获取热门标签列表（按关联数量降序）
     *
     * @param limit 返回数量上限
     * @return 标签列表
     */
    public List<Tag> getTopTags(int limit) {
        return tagMapper.selectTopTags(limit);
    }
}
