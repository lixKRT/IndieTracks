package com.indietracks.backend.service;

import com.indietracks.backend.dto.LoginRequest;
import com.indietracks.backend.dto.RegisterRequest;
import com.indietracks.backend.dto.UserDTO;
import com.indietracks.backend.entity.User;
import com.indietracks.backend.mapper.UserMapper;
import com.indietracks.backend.util.JwtUtil;
import com.indietracks.backend.util.UrlPresignHelper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final UrlPresignHelper urlPresign;

    public AuthService(UserMapper userMapper, PasswordEncoder passwordEncoder,
                       JwtUtil jwtUtil, UrlPresignHelper urlPresign) {
        this.userMapper = userMapper;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtil = jwtUtil;
        this.urlPresign = urlPresign;
    }

    public UserDTO register(RegisterRequest req) {
        Long usernameCount = userMapper.selectCount(
                new LambdaQueryWrapper<User>().eq(User::getUsername, req.getUsername()));
        if (usernameCount > 0) throw new RuntimeException("用户名已存在");

        Long emailCount = userMapper.selectCount(
                new LambdaQueryWrapper<User>().eq(User::getEmail, req.getEmail()));
        if (emailCount > 0) throw new RuntimeException("邮箱已被注册");

        User user = new User();
        user.setUsername(req.getUsername());
        user.setEmail(req.getEmail());
        user.setPassword_hash(passwordEncoder.encode(req.getPassword()));
        user.setUser_role("normal");
        userMapper.insert(user);

        return toDTO(user);
    }

    public UserDTO login(LoginRequest req) {
        User user = userMapper.selectOne(
                new LambdaQueryWrapper<User>()
                        .eq(User::getUsername, req.getAccount())
                        .or()
                        .eq(User::getEmail, req.getAccount()));

        if (user == null) throw new RuntimeException("用户不存在");
        if (!passwordEncoder.matches(req.getPassword(), user.getPassword_hash()))
            throw new RuntimeException("密码错误");

        return toDTO(user);
    }

    public String generateToken(UserDTO user, boolean rememberMe) {
        return jwtUtil.generateToken(user.getUser_id(), user.getUsername(), rememberMe);
    }

    public UserDTO getUserById(Integer userId) {
        User user = userMapper.selectById(userId);
        if (user == null) return null;
        UserDTO dto = toDTO(user);
        urlPresign.presignUserDTO(dto);
        return dto;
    }

    public void updateAvatar(Integer userId, String objectKey) {
        User user = userMapper.selectById(userId);
        if (user != null) {
            user.setAvatar_url(objectKey);
            userMapper.updateById(user);
        }
    }

    private UserDTO toDTO(User user) {
        UserDTO dto = new UserDTO();
        dto.setUser_id(user.getUser_id());
        dto.setUsername(user.getUsername());
        dto.setAvatar_url(user.getAvatar_url());
        dto.setUser_role(user.getUser_role());
        return dto;
    }
}
