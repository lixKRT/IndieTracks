package com.indietracks.backend.dto;

import lombok.Data;

import java.util.List;

@Data
public class CircleDetail {
    private Integer circle_id;
    private String name;
    private String logo_url;
    private String description;
    private List<String> representative_tags;
    private List<AlbumListItem> albums;
    private List<CircleMember> members;

    @Data
    public static class CircleMember {
        private Integer user_id;
        private String username;
        private String avatar_url;
        private String user_role;
    }
}
