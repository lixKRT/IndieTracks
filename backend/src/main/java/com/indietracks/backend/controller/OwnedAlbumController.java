package com.indietracks.backend.controller;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.service.OwnedAlbumService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/purchases")
public class OwnedAlbumController {

    private final OwnedAlbumService ownedAlbumService;

    public OwnedAlbumController(OwnedAlbumService ownedAlbumService) {
        this.ownedAlbumService = ownedAlbumService;
    }

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
