package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("circles")
public class Circle {
    @TableId(type = IdType.AUTO)
    private Integer circle_id;
    private Integer dizzylab_labelid;
    private String name;
    private String description;
    private String logo_url;
    private Integer owner_user_id;
    private Integer member_count;
}
