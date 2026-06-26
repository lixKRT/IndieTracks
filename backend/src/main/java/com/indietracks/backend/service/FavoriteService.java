package com.indietracks.backend.service;

import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.mapper.FavoriteMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.stereotype.Service;

import java.util.List;

/** 收藏服务 — 收藏/取消收藏、查询已收藏列表 */
@Service
public class FavoriteService {

    private final FavoriteMapper favoriteMapper;
    private final UrlPresignHelper urlPresign;

    public FavoriteService(FavoriteMapper favoriteMapper, UrlPresignHelper urlPresign) {
        this.favoriteMapper = favoriteMapper;
        this.urlPresign = urlPresign;
    }

    public List<AlbumListItem> getFavorites(Integer userId) {
        List<AlbumListItem> albums = favoriteMapper.selectFavoriteAlbums(userId);
        urlPresign.presignAlbumList(albums);
        return albums;
    }

    public void addFavorite(Integer userId, Integer albumId) {
        favoriteMapper.insertFavorite(userId, albumId);
    }

    public void removeFavorite(Integer userId, Integer albumId) {
        favoriteMapper.deleteFavorite(userId, albumId);
    }

    public boolean isFavorited(Integer userId, Integer albumId) {
        return favoriteMapper.countFavorite(userId, albumId) > 0;
    }
}
