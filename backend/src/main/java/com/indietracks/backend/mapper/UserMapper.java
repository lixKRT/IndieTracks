package com.indietracks.backend.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.entity.User;
import org.apache.ibatis.annotations.Mapper;

/** 用户（users 表），role: normal/pro/staff；无自定义方法，使用 BaseMapper 默认 CRUD */
@Mapper
public interface UserMapper extends BaseMapper<User> {
}
