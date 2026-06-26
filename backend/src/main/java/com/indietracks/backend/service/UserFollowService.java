package com.indietracks.backend.service;

import com.indietracks.backend.dto.UserDTO;
import com.indietracks.backend.mapper.UserFollowMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 用户关注服务 — 关注/取关操作、查询关注状态与关注列表
 */
@Service
public class UserFollowService {

    private final UserFollowMapper userFollowMapper;
    private final UrlPresignHelper urlPresign;

    public UserFollowService(UserFollowMapper userFollowMapper, UrlPresignHelper urlPresign) {
        this.userFollowMapper = userFollowMapper;
        this.urlPresign = urlPresign;
    }

    /**
     * 关注目标用户
     *
     * @param userId   当前用户 ID
     * @param targetId 目标用户 ID
     */
    public void follow(Integer userId, Integer targetId) {
        userFollowMapper.insertFollow(userId, targetId);
    }

    /**
     * 取消关注目标用户
     *
     * @param userId   当前用户 ID
     * @param targetId 目标用户 ID
     */
    public void unfollow(Integer userId, Integer targetId) {
        userFollowMapper.deleteFollow(userId, targetId);
    }

    /**
     * 判断当前用户是否已关注目标用户
     *
     * @param userId   当前用户 ID
     * @param targetId 目标用户 ID
     * @return true 表示已关注
     */
    public boolean isFollowing(Integer userId, Integer targetId) {
        return userFollowMapper.countFollow(userId, targetId) > 0;
    }

    /**
     * 获取当前用户的关注列表，头像统一预签名
     *
     * @param userId 用户 ID
     * @return 关注用户列表（含预签名头像 URL）
     */
    public List<UserDTO> getFollowedUsers(Integer userId) {
        List<UserDTO> users = userFollowMapper.selectFollowedUsers(userId);
        urlPresign.presignUserDTOList(users);
        return users;
    }
}
