package com.indietracks.backend.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.dto.CircleDetail;
import com.indietracks.backend.dto.CircleListItem;
import com.indietracks.backend.entity.Circle;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface CircleMapper extends BaseMapper<Circle> {

    List<CircleListItem> selectCircleList();

    List<CircleListItem> selectCircleListPaged(@Param("offset") int offset, @Param("limit") int limit);

    int selectCircleCount();

    List<CircleDetail.CircleMember> selectMembersByCircleId(@Param("circle_id") Integer circle_id);
}
