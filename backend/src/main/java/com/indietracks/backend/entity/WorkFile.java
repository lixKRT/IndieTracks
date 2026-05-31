package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("work_files")
public class WorkFile {
    @TableId(type = IdType.AUTO)
    private Integer file_id;
    private Integer album_id;
    private String file_name;
    private String object_key;
    private String file_type;
    private String track_length;
    private Long file_size;
    private Integer sort_order;
}
