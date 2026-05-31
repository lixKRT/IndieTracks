package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("circle_follows")
public class CircleFollow {
    private Integer user_id;
    private Integer circle_id;
    private LocalDateTime created_at;
}
