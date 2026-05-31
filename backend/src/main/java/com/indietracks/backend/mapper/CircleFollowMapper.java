package com.indietracks.backend.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.dto.CircleListItem;
import com.indietracks.backend.entity.CircleFollow;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface CircleFollowMapper extends BaseMapper<CircleFollow> {

    int insertFollow(@Param("user_id") Integer user_id, @Param("circle_id") Integer circle_id);

    int deleteFollow(@Param("user_id") Integer user_id, @Param("circle_id") Integer circle_id);

    int countFollow(@Param("user_id") Integer user_id, @Param("circle_id") Integer circle_id);

    List<CircleListItem> selectFollowedCircles(@Param("user_id") Integer user_id);
}
