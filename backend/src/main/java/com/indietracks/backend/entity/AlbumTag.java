package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("album_tags")
public class AlbumTag {
    private Integer album_id;
    private Integer tag_id;
}
