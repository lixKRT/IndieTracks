package com.indietracks.backend.controller;

import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.service.CartService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/cart")
public class CartController {

    private final CartService cartService;

    public CartController(CartService cartService) {
        this.cartService = cartService;
    }

    @GetMapping
    public ResponseEntity<List<AlbumListItem>> getCart(@CurrentUser Integer userId) {
        return ResponseEntity.ok(cartService.getCartItems(userId));
    }

    @PostMapping("/{albumId}")
    public ResponseEntity<?> addToCart(@PathVariable Integer albumId, @CurrentUser Integer userId) {
        cartService.addToCart(userId, albumId);
        return ResponseEntity.ok(Map.of("message", "已加入购物车"));
    }

    @DeleteMapping("/{albumId}")
    public ResponseEntity<?> removeFromCart(@PathVariable Integer albumId, @CurrentUser Integer userId) {
        cartService.removeFromCart(userId, albumId);
        return ResponseEntity.ok(Map.of("message", "已移除"));
    }

    @GetMapping("/count")
    public ResponseEntity<Map<String, Integer>> getCartCount(@CurrentUser Integer userId) {
        return ResponseEntity.ok(Map.of("count", cartService.getCartCount(userId)));
    }

    @GetMapping("/{albumId}/status")
    public ResponseEntity<Map<String, Boolean>> checkInCart(@PathVariable Integer albumId, @CurrentUser Integer userId) {
        boolean inCart = cartService.isInCart(userId, albumId);
        return ResponseEntity.ok(Map.of("in_cart", inCart));
    }

    @PostMapping("/checkout")
    public ResponseEntity<?> checkout(@CurrentUser Integer userId, @RequestBody Map<String, List<Integer>> body) {
        List<Integer> albumIds = body.get("album_ids");
        if (albumIds == null || albumIds.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "请选择要结算的专辑"));
        }
        cartService.checkout(userId, albumIds);
        return ResponseEntity.ok(Map.of("message", "购买成功"));
    }
}
