package com.indietracks.backend.service;

import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.mapper.CartMapper;
import com.indietracks.backend.mapper.OwnedAlbumMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class CartService {

    private final CartMapper cartMapper;
    private final OwnedAlbumMapper ownedAlbumMapper;
    private final UrlPresignHelper urlPresign;

    public CartService(CartMapper cartMapper, OwnedAlbumMapper ownedAlbumMapper, UrlPresignHelper urlPresign) {
        this.cartMapper = cartMapper;
        this.ownedAlbumMapper = ownedAlbumMapper;
        this.urlPresign = urlPresign;
    }

    public List<AlbumListItem> getCartItems(Integer userId) {
        List<AlbumListItem> albums = cartMapper.selectCartAlbums(userId);
        urlPresign.presignAlbumList(albums);
        return albums;
    }

    public void addToCart(Integer userId, Integer albumId) {
        // 检查是否已拥有
        if (ownedAlbumMapper.countOwnedAlbum(userId, albumId) > 0) {
            return; // 已拥有，不加入购物车
        }
        cartMapper.insertCartItem(userId, albumId);
    }

    public void removeFromCart(Integer userId, Integer albumId) {
        cartMapper.deleteCartItem(userId, albumId);
    }

    public boolean isInCart(Integer userId, Integer albumId) {
        return cartMapper.countCartItem(userId, albumId) > 0;
    }

    public int getCartCount(Integer userId) {
        return cartMapper.countCartItems(userId);
    }

    @Transactional
    public void checkout(Integer userId, List<Integer> albumIds) {
        // 模拟支付延迟
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        // 批量购买
        for (Integer albumId : albumIds) {
            ownedAlbumMapper.insertOwnedAlbum(userId, albumId);
            cartMapper.deleteCartItem(userId, albumId);
        }
    }
}
