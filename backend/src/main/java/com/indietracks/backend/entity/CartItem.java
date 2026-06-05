package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("cart_items")
public class CartItem {
    private Integer user_id;
    private Integer album_id;
    private LocalDateTime created_at;
}
