package com.indietracks.backend.mapper;

import com.indietracks.backend.dto.AlbumListItem;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.entity.Favorite;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface FavoriteMapper extends BaseMapper<Favorite> {

    List<AlbumListItem> selectFavoriteAlbums(@Param("user_id") Integer user_id);

    int insertFavorite(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);

    int deleteFavorite(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);

    int countFavorite(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);
}
