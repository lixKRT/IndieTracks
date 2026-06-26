package com.indietracks.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 社团实体，对应 circles 表。
 * <p>社团（Circle）对应 dizzylab 上的厂牌/社团页面，可发布多张专辑。</p>
 */
@Data
@TableName("circles")
public class Circle {
    /** 主键，自增 */
    @TableId(type = IdType.AUTO)
    private Integer circle_id;

    /** dizzylab 来源 labelid，UNIQUE，用于爬虫去重 */
    private Integer dizzylab_labelid;

    /** 社团名称 */
    private String name;

    /** 社团简介 */
    private String description;

    /** Logo 图片 MinIO 对象 Key，前端需拼接完整访问地址 */
    private String logo_url;

    /** 社团拥有者用户 ID，关联 users 表，用户删除后 SET NULL，可为 null */
    private Integer owner_user_id;

    /** 社团成员数，默认 0 */
    private Integer member_count;
}
