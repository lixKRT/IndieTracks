package com.indietracks.backend.service;

import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.mapper.CartMapper;
import com.indietracks.backend.mapper.OwnedAlbumMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * 购物车服务。
 * <p>
 * 提供购物车的增删查操作、已购去重校验以及模拟结算功能。
 * 购物车数据存储于 cart 表，结算后写入 owned_albums 表并清除对应购物车记录。
 * </p>
 *
 * <h3>依赖说明</h3>
 * <ul>
 *   <li>{@link CartMapper} — 购物车记录的 CRUD</li>
 *   <li>{@link OwnedAlbumMapper} — 用户已购专辑查询与写入</li>
 *   <li>{@link UrlPresignHelper} — MinIO 对象 URL 预签名</li>
 * </ul>
 *
 * @see CartMapper
 * @see OwnedAlbumMapper
 */
@Service
public class CartService {

    private final CartMapper cartMapper;
    private final OwnedAlbumMapper ownedAlbumMapper;
    private final UrlPresignHelper urlPresign;

    /**
     * 构造注入所有依赖。
     *
     * @param cartMapper        购物车 Mapper
     * @param ownedAlbumMapper  已购专辑 Mapper
     * @param urlPresign        URL 预签名工具
     */
    public CartService(CartMapper cartMapper, OwnedAlbumMapper ownedAlbumMapper, UrlPresignHelper urlPresign) {
        this.cartMapper = cartMapper;
        this.ownedAlbumMapper = ownedAlbumMapper;
        this.urlPresign = urlPresign;
    }

    /**
     * 获取用户购物车中的所有专辑。
     * <p>
     * 查询结果中的封面 URL 会通过 {@link UrlPresignHelper} 转换为带签名的临时访问地址。
     * </p>
     *
     * @param userId 用户 ID
     * @return 购物车专辑列表（已预签名）
     */
    public List<AlbumListItem> getCartItems(Integer userId) {
        List<AlbumListItem> albums = cartMapper.selectCartAlbums(userId);
        urlPresign.presignAlbumList(albums);
        return albums;
    }

    /**
     * 将专辑加入购物车。
     * <p>
     * 会先校验用户是否已购买该专辑，若已拥有则静默跳过，不会重复添加。
     * </p>
     *
     * @param userId  用户 ID
     * @param albumId 专辑 ID
     */
    public void addToCart(Integer userId, Integer albumId) {
        // 检查是否已拥有
        if (ownedAlbumMapper.countOwnedAlbum(userId, albumId) > 0) {
            return; // 已拥有，不加入购物车
        }
        cartMapper.insertCartItem(userId, albumId);
    }

    /**
     * 从购物车中移除指定专辑。
     *
     * @param userId  用户 ID
     * @param albumId 专辑 ID
     */
    public void removeFromCart(Integer userId, Integer albumId) {
        cartMapper.deleteCartItem(userId, albumId);
    }

    /**
     * 判断指定专辑是否已在用户购物车中。
     *
     * @param userId  用户 ID
     * @param albumId 专辑 ID
     * @return {@code true} 表示已在购物车中
     */
    public boolean isInCart(Integer userId, Integer albumId) {
        return cartMapper.countCartItem(userId, albumId) > 0;
    }

    /**
     * 获取用户购物车中的专辑数量。
     *
     * @param userId 用户 ID
     * @return 购物车专辑数量
     */
    public int getCartCount(Integer userId) {
        return cartMapper.countCartItems(userId);
    }

    /**
     * 模拟结算（购买）流程。
     * <p>
     * 在同一事务内完成以下操作：
     * <ol>
     *   <li>模拟 2 秒支付延迟以模拟真实支付体验</li>
     *   <li>将每个专辑写入 owned_albums 表（标记为已购）</li>
     *   <li>从 cart 表中移除对应的购物车记录</li>
     * </ol>
     * </p>
     *
     * @param userId   用户 ID
     * @param albumIds 待结算的专辑 ID 列表
     */
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
