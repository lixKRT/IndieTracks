package com.indietracks.backend.controller;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.service.FavoriteService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** 收藏接口 — 收藏列表、收藏/取消收藏、查询收藏状态 */
@RestController
@RequestMapping("/api/favorites")
public class FavoriteController {

    private final FavoriteService favoriteService;

    public FavoriteController(FavoriteService favoriteService) {
        this.favoriteService = favoriteService;
    }

    @GetMapping
    public ResponseEntity<List<AlbumListItem>> getFavorites(@CurrentUser Integer userId) {
        return ResponseEntity.ok(favoriteService.getFavorites(userId));
    }

    @PostMapping("/{albumId}")
    public ResponseEntity<?> addFavorite(@PathVariable Integer albumId, @CurrentUser Integer userId) {
        favoriteService.addFavorite(userId, albumId);
        return ResponseEntity.ok(Map.of("message", "已收藏"));
    }

    @DeleteMapping("/{albumId}")
    public ResponseEntity<?> removeFavorite(@PathVariable Integer albumId, @CurrentUser Integer userId) {
        favoriteService.removeFavorite(userId, albumId);
        return ResponseEntity.ok(Map.of("message", "已取消收藏"));
    }

    @GetMapping("/{albumId}/status")
    public ResponseEntity<Map<String, Boolean>> checkFavorite(@PathVariable Integer albumId, @CurrentUser Integer userId) {
        boolean favorited = favoriteService.isFavorited(userId, albumId);
        return ResponseEntity.ok(Map.of("favorited", favorited));
    }
}
