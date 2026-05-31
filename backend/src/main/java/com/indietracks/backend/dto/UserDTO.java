package com.indietracks.backend.dto;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class UserDTO {
    private Integer user_id;
    private String username;
    private String avatar_url;
    private String user_role;
    private String circle_name;
}
