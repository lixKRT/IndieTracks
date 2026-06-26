package com.indietracks.backend.service;

import com.indietracks.backend.dto.UserDTO;
import com.indietracks.backend.entity.User;
import com.indietracks.backend.mapper.UserMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.stereotype.Service;

/**
 * 用户服务 — 根据 ID 查询用户信息（脱敏 DTO）
 */
@Service
public class UserService {

    private final UserMapper userMapper;
    private final UrlPresignHelper urlPresign;

    public UserService(UserMapper userMapper, UrlPresignHelper urlPresign) {
        this.userMapper = userMapper;
        this.urlPresign = urlPresign;
    }

    /**
     * 根据用户 ID 查询用户信息，返回脱敏 DTO（不含密码等敏感字段）
     * 头像 URL 经 MinIO 预签名后可直接访问
     *
     * @param userId 用户 ID
     * @return 用户 DTO；用户不存在时返回 null
     */
    public UserDTO getUserById(Integer userId) {
        User user = userMapper.selectById(userId);
        if (user == null) return null;
        UserDTO dto = new UserDTO();
        dto.setUser_id(user.getUser_id());
        dto.setUsername(user.getUsername());
        dto.setAvatar_url(user.getAvatar_url());
        dto.setUser_role(user.getUser_role());
        urlPresign.presignUserDTO(dto);
        return dto;
    }
}
