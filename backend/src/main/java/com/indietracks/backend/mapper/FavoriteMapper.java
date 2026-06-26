package com.indietracks.backend.mapper;

import com.indietracks.backend.dto.AlbumListItem;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.entity.Favorite;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/** 用户收藏专辑（favorites 表） */
@Mapper
public interface FavoriteMapper extends BaseMapper<Favorite> {

    /** 返回用户收藏的专辑列表（DTO，含社团/标签聚合） */
    List<AlbumListItem> selectFavoriteAlbums(@Param("user_id") Integer user_id);

    /** 新增用户收藏记录 */
    int insertFavorite(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);

    /** 取消用户对专辑的收藏 */
    int deleteFavorite(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);

    /** 判断用户是否已收藏该专辑（返回 0 或 1） */
    int countFavorite(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);
}
