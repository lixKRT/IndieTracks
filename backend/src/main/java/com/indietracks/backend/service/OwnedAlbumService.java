package com.indietracks.backend.service;

import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.mapper.OwnedAlbumMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class OwnedAlbumService {

    private final OwnedAlbumMapper ownedAlbumMapper;
    private final UrlPresignHelper urlPresign;

    public OwnedAlbumService(OwnedAlbumMapper ownedAlbumMapper, UrlPresignHelper urlPresign) {
        this.ownedAlbumMapper = ownedAlbumMapper;
        this.urlPresign = urlPresign;
    }

    public List<AlbumListItem> getOwnedAlbums(Integer userId) {
        List<AlbumListItem> albums = ownedAlbumMapper.selectOwnedAlbums(userId);
        urlPresign.presignAlbumList(albums);
        return albums;
    }

    public void purchaseAlbum(Integer userId, Integer albumId) {
        // 模拟支付延迟
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        ownedAlbumMapper.insertOwnedAlbum(userId, albumId);
    }

    public boolean isOwned(Integer userId, Integer albumId) {
        return ownedAlbumMapper.countOwnedAlbum(userId, albumId) > 0;
    }
}
