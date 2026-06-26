package com.indietracks.backend.mapper;

import com.indietracks.backend.dto.AlbumListItem;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.entity.CartItem;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/** 购物车（cart_items 表），临时关联，结算后清空 */
@Mapper
public interface CartMapper extends BaseMapper<CartItem> {

    /** 返回用户购物车中的专辑列表（DTO，含社团/标签聚合） */
    List<AlbumListItem> selectCartAlbums(@Param("user_id") Integer user_id);

    /** 添加商品到购物车，已存在时静默跳过 */
    int insertCartItem(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);

    int deleteCartItem(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);

    /** 判断某专辑是否已在购物车 */
    int countCartItem(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);

    /** 用户购物车总条数 */
    int countCartItems(@Param("user_id") Integer user_id);

    /** 清空用户购物车（结算成功后调用） */
    int clearCart(@Param("user_id") Integer user_id);
}
