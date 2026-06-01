package com.indietracks.backend.mapper;

import com.indietracks.backend.dto.AlbumListItem;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.entity.OwnedAlbum;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface OwnedAlbumMapper extends BaseMapper<OwnedAlbum> {

    List<AlbumListItem> selectOwnedAlbums(@Param("user_id") Integer user_id);

    int insertOwnedAlbum(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);

    int countOwnedAlbum(@Param("user_id") Integer user_id, @Param("album_id") Integer album_id);
}
