package com.indietracks.backend.controller;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.service.OwnedAlbumService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/** 已购专辑接口 — 查询列表、购买、检查购买状态 */
@RestController
@RequestMapping("/api/purchases")
public class OwnedAlbumController {

    private final OwnedAlbumService ownedAlbumService;

    public OwnedAlbumController(OwnedAlbumService ownedAlbumService) {
        this.ownedAlbumService = ownedAlbumService;
    }

    // @CurrentUser: 自定义注解，从 JWT 中提取当前登录用户 ID（下同）
    @GetMapping
    public ResponseEntity<List<AlbumListItem>> getOwnedAlbums(@CurrentUser Integer userId) {
        return ResponseEntity.ok(ownedAlbumService.getOwnedAlbums(userId));
    }

    @PostMapping("/{albumId}")
    public ResponseEntity<?> purchaseAlbum(@PathVariable Integer albumId, @CurrentUser Integer userId) {
        ownedAlbumService.purchaseAlbum(userId, albumId);
        return ResponseEntity.ok(Map.of("message", "购买成功"));
    }

    @GetMapping("/{albumId}/status")
    public ResponseEntity<Map<String, Boolean>> checkOwned(@PathVariable Integer albumId, @CurrentUser Integer userId) {
        boolean owned = ownedAlbumService.isOwned(userId, albumId);
        return ResponseEntity.ok(Map.of("owned", owned));
    }
}
