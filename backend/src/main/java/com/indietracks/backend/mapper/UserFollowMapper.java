package com.indietracks.backend.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.dto.UserDTO;
import com.indietracks.backend.entity.UserFollow;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface UserFollowMapper extends BaseMapper<UserFollow> {

    int insertFollow(@Param("user_id") Integer user_id, @Param("followed_user_id") Integer followed_user_id);

    int deleteFollow(@Param("user_id") Integer user_id, @Param("followed_user_id") Integer followed_user_id);

    int countFollow(@Param("user_id") Integer user_id, @Param("followed_user_id") Integer followed_user_id);

    List<UserDTO> selectFollowedUsers(@Param("user_id") Integer user_id);
}
