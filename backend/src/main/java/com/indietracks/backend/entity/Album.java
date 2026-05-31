package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("albums")
public class Album {
    @TableId(type = IdType.AUTO)
    private Integer album_id;
    private String dizzylab_id;
    private String title;
    private String info_title;
    private String info_content;
    private BigDecimal price;
    private String cover_url;
    private LocalDateTime publish_date;
}
