package com.indietracks.backend.service;

import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.mapper.OwnedAlbumMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 用户已购专辑服务 — 查询已购列表、模拟购买、判断是否已购
 */
@Service
public class OwnedAlbumService {

    private final OwnedAlbumMapper ownedAlbumMapper;
    private final UrlPresignHelper urlPresign;

    public OwnedAlbumService(OwnedAlbumMapper ownedAlbumMapper, UrlPresignHelper urlPresign) {
        this.ownedAlbumMapper = ownedAlbumMapper;
        this.urlPresign = urlPresign;
    }

    /**
     * 获取用户的已购专辑列表，封面图统一预签名
     *
     * @param userId 用户 ID
     * @return 已购专辑列表（含预签名封面 URL）
     */
    public List<AlbumListItem> getOwnedAlbums(Integer userId) {
        List<AlbumListItem> albums = ownedAlbumMapper.selectOwnedAlbums(userId);
        urlPresign.presignAlbumList(albums);
        return albums;
    }

    /**
     * 模拟购买专辑：延迟 2 秒模拟支付流程后写入购买记录
     *
     * @param userId  用户 ID
     * @param albumId 专辑 ID
     */
    public void purchaseAlbum(Integer userId, Integer albumId) {
        // 模拟支付延迟
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        ownedAlbumMapper.insertOwnedAlbum(userId, albumId);
    }

    /**
     * 判断用户是否已购买指定专辑
     *
     * @param userId  用户 ID
     * @param albumId 专辑 ID
     * @return true 表示已购买
     */
    public boolean isOwned(Integer userId, Integer albumId) {
        return ownedAlbumMapper.countOwnedAlbum(userId, albumId) > 0;
    }
}
