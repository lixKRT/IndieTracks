package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/** 标签实体，用于专辑分类与筛选 */
@Data
@TableName("tags")
public class Tag {
    @TableId(type = IdType.AUTO)
    private Integer tag_id;
    private String name;               // 标签名称，UNIQUE NOT NULL
}
