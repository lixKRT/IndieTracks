package com.indietracks.backend.mapper;

import com.indietracks.backend.dto.AlbumListItem;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.entity.CartItem;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface CartMapper extends BaseMapper<CartItem> {

    List<AlbumListItem> selectCartAlbums(@Param("user_id") Integer user_id);

    int insertCartItem(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);

    int deleteCartItem(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);

    int countCartItem(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);

    int countCartItems(@Param("user_id") Integer user_id);

    int clearCart(@Param("user_id") Integer user_id);
}
