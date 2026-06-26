package com.indietracks.backend.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.indietracks.backend.annotation.CurrentUser;
import com.indietracks.backend.dto.AlbumDetail;
import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.dto.CommentRequest;
import com.indietracks.backend.dto.PagedResponse;
import com.indietracks.backend.service.AlbumService;
import com.indietracks.backend.service.CommentService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/** 专辑相关接口 — 列表、详情、评论、推荐 */
@RestController
@RequestMapping("/api/albums")
public class AlbumController {

    private final AlbumService albumService;
    private final CommentService commentService;

    public AlbumController(AlbumService albumService, CommentService commentService) {
        this.albumService = albumService;
        this.commentService = commentService;
    }

    @GetMapping
    public ResponseEntity<PagedResponse<AlbumListItem>> getAlbums(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "12") int page_size,
            @RequestParam(required = false) String tag,      // 可选筛选，标签名称
            @RequestParam(required = false) String search,   // 可选筛选，关键词搜索
            @RequestParam(required = false) String price,    // 可选筛选，价格区间
            @RequestParam(defaultValue = "publish_date_desc") String sort) { // 可选值: publish_date_desc, price_asc, price_desc

        IPage<AlbumListItem> result = albumService.getAlbumList(page, page_size, tag, search, price, sort);
        return ResponseEntity.ok(PagedResponse.of(
                result.getRecords(), result.getTotal(), result.getCurrent(), result.getSize()));
    }

    @GetMapping("/{id}")
    public ResponseEntity<AlbumDetail> getAlbum(@PathVariable Integer id) {
        AlbumDetail detail = albumService.getAlbumDetail(id);
        if (detail == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(detail);
    }

    @GetMapping("/{id}/comments")
    public ResponseEntity<PagedResponse<AlbumDetail.CommentInfo>> getComments(
            @PathVariable Integer id,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "5") int page_size) {
        return ResponseEntity.ok(commentService.getCommentsPaged(id, page, page_size));
    }

    @PostMapping("/{id}/comments")
    public ResponseEntity<?> addComment(@PathVariable Integer id,
                                        @Valid @RequestBody CommentRequest req,
                                        @CurrentUser Integer userId) {
        commentService.addComment(id, userId, req.getContent());
        // 返回列表而非单条，前端直接替换当前评论列表
        return ResponseEntity.ok(commentService.getCommentsPaged(id, 1, 5));
    }

    @GetMapping("/{id}/recommendations")
    public ResponseEntity<List<AlbumListItem>> getRecommendations(@PathVariable Integer id) { // 随机推荐，排除当前专辑
        List<AlbumListItem> recommendations = albumService.getRandomRecommendations(id, 5);
        return ResponseEntity.ok(recommendations);
    }
}
