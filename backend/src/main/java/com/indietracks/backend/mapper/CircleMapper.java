package com.indietracks.backend.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.dto.CircleDetail;
import com.indietracks.backend.dto.CircleListItem;
import com.indietracks.backend.entity.Circle;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/** 社团（circles 表），dizzylab_labelid 去重 */
@Mapper
public interface CircleMapper extends BaseMapper<Circle> {

    /** 返回全部社团列表（DTO，含成员/专辑数等聚合） */
    List<CircleListItem> selectCircleList();

    /** 分页查询社团列表（手动 offset/limit，非 MyBatis-Plus Page） */
    List<CircleListItem> selectCircleListPaged(@Param("offset") int offset, @Param("limit") int limit);

    /** 社团总数，配合 selectCircleListPaged 计算分页 */
    int selectCircleCount();

    /** 查询社团下的成员列表（DTO，含用户公开信息） */
    List<CircleDetail.CircleMember> selectMembersByCircleId(@Param("circle_id") Integer circle_id);

    /** 查询用户所属的社团 ID 列表 */
    List<Integer> selectCircleIdsByUserId(@Param("user_id") Integer user_id);
}
