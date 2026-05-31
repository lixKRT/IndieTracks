package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("user_circles")
public class UserCircle {
    private Integer user_id;
    private Integer circle_id;
}
