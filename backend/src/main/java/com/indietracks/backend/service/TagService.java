package com.indietracks.backend.service;

import com.indietracks.backend.entity.Tag;
import com.indietracks.backend.mapper.TagMapper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class TagService {

    private final TagMapper tagMapper;

    public TagService(TagMapper tagMapper) {
        this.tagMapper = tagMapper;
    }

    public List<Tag> getAllTags() {
        return tagMapper.selectList(null);
    }
}
