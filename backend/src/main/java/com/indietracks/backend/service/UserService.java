package com.indietracks.backend.service;

import com.indietracks.backend.dto.UserDTO;
import com.indietracks.backend.entity.User;
import com.indietracks.backend.mapper.UserMapper;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private final UserMapper userMapper;
    private final MinioService minioService;

    public UserService(UserMapper userMapper, MinioService minioService) {
        this.userMapper = userMapper;
        this.minioService = minioService;
    }

    public UserDTO getUserById(Integer userId) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            return null;
        }
        UserDTO dto = new UserDTO();
        dto.setUser_id(user.getUser_id());
        dto.setUsername(user.getUsername());
        dto.setAvatar_url(minioService.getPresignedUrl(user.getAvatar_url()));
        dto.setUser_role(user.getUser_role());
        return dto;
    }
}
