package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("album_circles")
public class AlbumCircle {
    private Integer album_id;
    private Integer circle_id;
}
