package com.indietracks.backend.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.dto.CircleListItem;
import com.indietracks.backend.entity.CircleFollow;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/** 用户关注社团（circle_follows 表） */
@Mapper
public interface CircleFollowMapper extends BaseMapper<CircleFollow> {

    /** 新增用户对社团的关注记录 */
    int insertFollow(@Param("user_id") Integer user_id, @Param("circle_id") Integer circle_id);

    /** 取消用户对社团的关注 */
    int deleteFollow(@Param("user_id") Integer user_id, @Param("circle_id") Integer circle_id);

    /** 判断用户是否已关注该社团（返回 0 或 1） */
    int countFollow(@Param("user_id") Integer user_id, @Param("circle_id") Integer circle_id);

    /** 返回用户关注的社团列表（DTO，含关注数等聚合字段） */
    List<CircleListItem> selectFollowedCircles(@Param("user_id") Integer user_id);
}
