package com.indietracks.backend.service;

import com.indietracks.backend.dto.UserDTO;
import com.indietracks.backend.mapper.UserFollowMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserFollowService {

    private final UserFollowMapper userFollowMapper;
    private final UrlPresignHelper urlPresign;

    public UserFollowService(UserFollowMapper userFollowMapper, UrlPresignHelper urlPresign) {
        this.userFollowMapper = userFollowMapper;
        this.urlPresign = urlPresign;
    }

    public void follow(Integer userId, Integer targetId) {
        userFollowMapper.insertFollow(userId, targetId);
    }

    public void unfollow(Integer userId, Integer targetId) {
        userFollowMapper.deleteFollow(userId, targetId);
    }

    public boolean isFollowing(Integer userId, Integer targetId) {
        return userFollowMapper.countFollow(userId, targetId) > 0;
    }

    public List<UserDTO> getFollowedUsers(Integer userId) {
        List<UserDTO> users = userFollowMapper.selectFollowedUsers(userId);
        urlPresign.presignUserDTOList(users);
        return users;
    }
}
