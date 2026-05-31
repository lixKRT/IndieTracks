package com.indietracks.backend.dto;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class AlbumListItem {
    private Integer album_id;
    private String title;
    private Integer circle_id;
    private String circle_name;
    private String circle_logo_url;
    private String cover_url;
    private String info_title;
    private String info_content;
    private BigDecimal price;
    private LocalDateTime publish_date;
    private List<String> tags;
    private Integer track_count;
}
