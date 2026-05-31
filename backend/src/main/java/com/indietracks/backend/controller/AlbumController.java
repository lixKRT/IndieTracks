package com.indietracks.backend.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.indietracks.backend.dto.AlbumDetail;
import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.service.AlbumService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/albums")
public class AlbumController {

    private final AlbumService albumService;

    public AlbumController(AlbumService albumService) {
        this.albumService = albumService;
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> getAlbums(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "12") int page_size,
            @RequestParam(required = false) String tag,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String price,
            @RequestParam(defaultValue = "publish_date_desc") String sort) {

        IPage<AlbumListItem> result = albumService.getAlbumList(page, page_size, tag, search, price, sort);

        Map<String, Object> response = new HashMap<>();
        response.put("data", result.getRecords());
        response.put("total", result.getTotal());
        response.put("page", result.getCurrent());
        response.put("page_size", result.getSize());
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<AlbumDetail> getAlbum(@PathVariable Integer id) {
        AlbumDetail detail = albumService.getAlbumDetail(id);
        if (detail == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(detail);
    }

    @GetMapping("/{id}/comments")
    public ResponseEntity<Map<String, Object>> getComments(
            @PathVariable Integer id,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "5") int page_size) {

        Map<String, Object> result = albumService.getComments(id, page, page_size);
        return ResponseEntity.ok(result);
    }
}
