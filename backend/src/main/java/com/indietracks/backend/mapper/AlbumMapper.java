package com.indietracks.backend.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.indietracks.backend.dto.AlbumDetail;
import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.entity.Album;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface AlbumMapper extends BaseMapper<Album> {

    IPage<AlbumListItem> selectAlbumList(Page<AlbumListItem> page,
                                         @Param("tag") String tag,
                                         @Param("search") String search,
                                         @Param("price") String price,
                                         @Param("sort") String sort);

    List<AlbumListItem> selectAlbumsByCircleId(@Param("circle_id") Integer circle_id);

    List<AlbumListItem> selectAlbumsByCircleIds(@Param("circleIds") List<Integer> circleIds);

    AlbumDetail.AlbumCircleInfo selectCircleByAlbumId(@Param("album_id") Integer album_id);

    List<AlbumDetail.TagInfo> selectTagsByAlbumId(@Param("album_id") Integer album_id);

    List<AlbumDetail.TrackInfo> selectTracksByAlbumId(@Param("album_id") Integer album_id);

    List<AlbumDetail.CommentInfo> selectCommentsByAlbumId(@Param("album_id") Integer album_id);

    List<AlbumDetail.CommentInfo> selectCommentsPage(@Param("album_id") Integer album_id,
                                                     @Param("limit") int limit,
                                                     @Param("offset") int offset);

    int countCommentsByAlbumId(@Param("album_id") Integer album_id);

    List<AlbumListItem> selectRandomAlbums(@Param("album_id") Integer album_id, @Param("limit") int limit);

    List<Integer> selectCircleIdsByAlbumId(@Param("album_id") Integer album_id);

    int insertAlbumCircle(@Param("album_id") Integer album_id, @Param("circle_id") Integer circle_id);
}
