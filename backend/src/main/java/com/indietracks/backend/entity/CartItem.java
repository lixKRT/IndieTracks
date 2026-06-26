package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/** 购物车实体，联合主键 (user_id, album_id)，结算后清空 */
@Data
@TableName("cart_items")
public class CartItem {
    private Integer user_id;       // 用户删除后 CASCADE
    private Integer album_id;      // 专辑删除后 CASCADE
    private LocalDateTime created_at;
}
