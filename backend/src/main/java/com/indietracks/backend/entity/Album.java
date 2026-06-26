package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 专辑实体，对应 albums 表。
 * <p>数据来源为 dizzylab.net 爬取，通过 dizzylab_id 去重。</p>
 */
@Data
@TableName("albums")
public class Album {
    /** 主键，自增 */
    @TableId(type = IdType.AUTO)
    private Integer album_id;

    /** dizzylab 来源 ID，UNIQUE NOT NULL，用于爬虫去重 */
    private String dizzylab_id;

    /** 专辑标题 */
    private String title;

    /** 专辑信息标题，可为 null */
    private String info_title;

    /** 专辑信息正文，可为 null，替代传统 description 字段 */
    private String info_content;

    /** 价格，DECIMAL(10,2)，使用 BigDecimal 避免浮点精度丢失 */
    private BigDecimal price;

    /** 封面图 MinIO 对象 Key，前端需拼接完整访问地址 */
    private String cover_url;

    /** 发布日期 */
    private LocalDateTime publish_date;
}
