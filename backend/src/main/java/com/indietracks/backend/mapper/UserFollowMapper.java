package com.indietracks.backend.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.dto.UserDTO;
import com.indietracks.backend.entity.UserFollow;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/** 用户关注用户（user_follows 表） */
@Mapper
public interface UserFollowMapper extends BaseMapper<UserFollow> {

    /** 新增用户关注关系记录 */
    int insertFollow(@Param("user_id") Integer user_id, @Param("followed_user_id") Integer followed_user_id);

    /** 取消用户对另一用户的关注 */
    int deleteFollow(@Param("user_id") Integer user_id, @Param("followed_user_id") Integer followed_user_id);

    /** 判断用户是否已关注目标用户（返回 0 或 1） */
    int countFollow(@Param("user_id") Integer user_id, @Param("followed_user_id") Integer followed_user_id);

    /** 返回用户关注的用户列表（DTO，脱敏后的公开信息） */
    List<UserDTO> selectFollowedUsers(@Param("user_id") Integer user_id);
}
