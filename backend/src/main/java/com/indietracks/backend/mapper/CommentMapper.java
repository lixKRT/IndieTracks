package com.indietracks.backend.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.indietracks.backend.dto.AlbumDetail;
import com.indietracks.backend.entity.Comment;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface CommentMapper extends BaseMapper<Comment> {

    /**
     * 分页查询专辑评论（含用户信息）
     */
    List<AlbumDetail.CommentInfo> selectCommentsPage(@Param("album_id") Integer album_id,
                                                     @Param("limit") int limit,
                                                     @Param("offset") int offset);

    /**
     * 专辑评论总数
     */
    int countCommentsByAlbumId(@Param("album_id") Integer album_id);
}
