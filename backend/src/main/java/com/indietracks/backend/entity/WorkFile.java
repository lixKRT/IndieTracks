package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/** 曲目文件实体 */
@Data
@TableName("work_files")
public class WorkFile {
    @TableId(type = IdType.AUTO)
    private Integer file_id;
    private Integer album_id;      // 专辑删除后 CASCADE
    private String file_name;
    private String object_key; // MinIO 对象 Key，前端拼接完整地址
    private String file_type; // 可选值: preview, full
    private String track_length; // 时长格式 "mm:ss"
    private Long file_size; // 字节数
    private Integer sort_order; // 同专辑内曲目排序序号
}
