package com.indietracks.backend.service;

import com.indietracks.backend.dto.AlbumDetail;
import com.indietracks.backend.dto.PagedResponse;
import com.indietracks.backend.entity.Comment;
import com.indietracks.backend.mapper.CommentMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CommentService {

    private final CommentMapper commentMapper;
    private final UrlPresignHelper urlPresign;

    public CommentService(CommentMapper commentMapper, UrlPresignHelper urlPresign) {
        this.commentMapper = commentMapper;
        this.urlPresign = urlPresign;
    }

    public PagedResponse<AlbumDetail.CommentInfo> getCommentsPaged(Integer albumId, int page, int pageSize) {
        int total = commentMapper.countCommentsByAlbumId(albumId);
        int offset = (page - 1) * pageSize;
        List<AlbumDetail.CommentInfo> comments = commentMapper.selectCommentsPage(albumId, pageSize, offset);
        urlPresign.presignComments(comments);
        return PagedResponse.of(comments, total, page, pageSize);
    }

    public AlbumDetail.CommentInfo addComment(Integer albumId, Integer userId, String content) {
        Comment comment = new Comment();
        comment.setAlbum_id(albumId);
        comment.setUser_id(userId);
        comment.setContent(content);
        commentMapper.insert(comment);
        List<AlbumDetail.CommentInfo> list = commentMapper.selectCommentsPage(albumId, 1, 0);
        if (!list.isEmpty()) {
            AlbumDetail.CommentInfo info = list.get(0);
            urlPresign.presignComments(list);
            return info;
        }
        return null;
    }

    public boolean updateComment(Integer commentId, Integer userId, String content) {
        Comment comment = commentMapper.selectById(commentId);
        if (comment == null || !comment.getUser_id().equals(userId)) return false;
        comment.setContent(content);
        commentMapper.updateById(comment);
        return true;
    }

    public boolean deleteComment(Integer commentId, Integer userId) {
        Comment comment = commentMapper.selectById(commentId);
        if (comment == null || !comment.getUser_id().equals(userId)) return false;
        commentMapper.deleteById(commentId);
        return true;
    }
}
