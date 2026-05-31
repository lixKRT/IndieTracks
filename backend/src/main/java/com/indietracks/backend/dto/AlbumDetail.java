package com.indietracks.backend.dto;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class AlbumDetail {
    private Integer album_id;
    private String title;
    private AlbumCircleInfo circle;
    private String cover_url;
    private BigDecimal price;
    private LocalDateTime publish_date;
    private String info_title;
    private String info_content;
    private List<TagInfo> tags;
    private List<TrackInfo> tracks;
    private List<CommentInfo> comments;

    @Data
    public static class AlbumCircleInfo {
        private Integer circle_id;
        private String name;
        private String logo_url;
    }

    @Data
    public static class TagInfo {
        private Integer tag_id;
        private String name;
    }

    @Data
    public static class TrackInfo {
        private Integer file_id;
        private String file_name;
        private String track_length;
        private Integer sort_order;
        private String file_type;
        private String preview_url;
    }

    @Data
    public static class CommentInfo {
        private Integer comment_id;
        private Integer user_id;
        private String username;
        private String avatar_url;
        private String content;
        private LocalDateTime created_at;
    }
}
