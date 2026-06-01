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
            @RequestParam(required = false) String tag,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String price,
            @RequestParam(defaultValue = "publish_date_desc") String sort) {

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
        return ResponseEntity.ok(commentService.getCommentsPaged(id, 1, 5));
    }

    @GetMapping("/{id}/recommendations")
    public ResponseEntity<List<AlbumListItem>> getRecommendations(@PathVariable Integer id) {
        List<AlbumListItem> recommendations = albumService.getRandomRecommendations(id, 5);
        return ResponseEntity.ok(recommendations);
    }
}
