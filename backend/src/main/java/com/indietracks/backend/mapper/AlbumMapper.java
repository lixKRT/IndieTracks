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

/** 专辑（albums 表），dizzylab_id 去重；info_title/info_content 替代 description */
@Mapper
public interface AlbumMapper extends BaseMapper<Album> {

    /**
     * 分页查询专辑列表
     * @param tag    可选筛选，标签名
     * @param search 可选筛选，关键字
     * @param price  可选筛选，价格区间
     * @param sort   可选值: publish_date_desc, price_asc, price_desc
     */
    IPage<AlbumListItem> selectAlbumList(Page<AlbumListItem> page,
                                         @Param("tag") String tag,
                                         @Param("search") String search,
                                         @Param("price") String price,
                                         @Param("sort") String sort);

    List<AlbumListItem> selectAlbumsByCircleId(@Param("circle_id") Integer circle_id);

    /** 按多个社团 ID 批量查询（用于社团详情页展示所有关联专辑） */
    List<AlbumListItem> selectAlbumsByCircleIds(@Param("circleIds") List<Integer> circleIds);

    /** 专辑所属社团（多对多，仅取第一条） */
    AlbumDetail.AlbumCircleInfo selectCircleByAlbumId(@Param("album_id") Integer album_id);

    List<AlbumDetail.TagInfo> selectTagsByAlbumId(@Param("album_id") Integer album_id);

    List<AlbumDetail.TrackInfo> selectTracksByAlbumId(@Param("album_id") Integer album_id);

    /** 用于专辑详情页的评论（limit 写死，非分页） */
    List<AlbumDetail.CommentInfo> selectCommentsByAlbumId(@Param("album_id") Integer album_id);

    /** 分页查询评论（含用户信息） */
    List<AlbumDetail.CommentInfo> selectCommentsPage(@Param("album_id") Integer album_id,
                                                     @Param("limit") int limit,
                                                     @Param("offset") int offset);

    int countCommentsByAlbumId(@Param("album_id") Integer album_id);

    /** 随机推荐，排除当前专辑（album_id），返回 limit 条 */
    List<AlbumListItem> selectRandomAlbums(@Param("album_id") Integer album_id, @Param("limit") int limit);

    /** 查询专辑关联的社团 ID 列表（album_circles 多对多） */
    List<Integer> selectCircleIdsByAlbumId(@Param("album_id") Integer album_id);

    /** 插入专辑-社团多对多关联，已存在时静默跳过 */
    int insertAlbumCircle(@Param("album_id") Integer album_id, @Param("circle_id") Integer circle_id);
}
