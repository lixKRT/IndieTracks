package com.indietracks.backend.controller;

import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.dto.CircleListItem;
import com.indietracks.backend.dto.UserDTO;
import com.indietracks.backend.service.CircleFollowService;
import com.indietracks.backend.service.FavoriteService;
import com.indietracks.backend.service.UserFollowService;
import com.indietracks.backend.service.UserService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/** 用户主页接口 — 查看任意用户的公开资料、收藏、关注的社团和用户 */
@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;
    private final FavoriteService favoriteService;
    private final CircleFollowService circleFollowService;
    private final UserFollowService userFollowService;

    public UserController(UserService userService, FavoriteService favoriteService,
                          CircleFollowService circleFollowService, UserFollowService userFollowService) {
        this.userService = userService;
        this.favoriteService = favoriteService;
        this.circleFollowService = circleFollowService;
        this.userFollowService = userFollowService;
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserDTO> getUser(@PathVariable Integer id) {
        UserDTO user = userService.getUserById(id);
        if (user == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(user);
    }

    @GetMapping("/{id}/favorites")
    public ResponseEntity<List<AlbumListItem>> getFavorites(@PathVariable Integer id) {
        return ResponseEntity.ok(favoriteService.getFavorites(id));
    }

    @GetMapping("/{id}/following-circles")
    public ResponseEntity<List<CircleListItem>> getFollowingCircles(@PathVariable Integer id) {
        return ResponseEntity.ok(circleFollowService.getFollowedCircles(id));
    }

    @GetMapping("/{id}/following-users")
    public ResponseEntity<List<UserDTO>> getFollowingUsers(@PathVariable Integer id) {
        return ResponseEntity.ok(userFollowService.getFollowedUsers(id));
    }
}
