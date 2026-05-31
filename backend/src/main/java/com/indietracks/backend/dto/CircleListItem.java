package com.indietracks.backend.dto;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
public class CircleListItem {
    private Integer circle_id;
    private String name;
    private String logo_url;
    private String description;
    private Integer album_count;
    private Integer member_count;
    private LocalDateTime latest_album_date;
    private List<String> representative_tags;
    private List<PreviewAlbum> preview_albums;

    @Data
    public static class PreviewAlbum {
        private Integer album_id;
        private String title;
        private String cover_url;
        private List<String> tags;
    }
}
