package com.indietracks.backend.mapper;

import com.indietracks.backend.dto.AlbumListItem;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.entity.OwnedAlbum;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/** 用户已购专辑（owned_albums 表） */
@Mapper
public interface OwnedAlbumMapper extends BaseMapper<OwnedAlbum> {

    /** 返回用户已购专辑列表（DTO，含社团/标签聚合） */
    List<AlbumListItem> selectOwnedAlbums(@Param("user_id") Integer user_id);

    /** 新增用户已购专辑记录 */
    int insertOwnedAlbum(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);

    /** 判断用户是否已拥有该专辑（返回 0 或 1） */
    int countOwnedAlbum(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);
}
