package com.indietracks.backend.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.entity.Tag;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/** 标签（tags 表） */
@Mapper
public interface TagMapper extends BaseMapper<Tag> {

    /**
     * 按使用次数排序，返回前 N 个标签
     */
    List<Tag> selectTopTags(@Param("limit") int limit);
}
