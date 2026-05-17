"""IndieTracks 爬虫 Item 定义（14 张表）。"""

import scrapy


class AlbumItem(scrapy.Item):
    album_id = scrapy.Field()         # SERIAL，插入后回填
    dizzylab_id = scrapy.Field()      # Dizzylab slug
    title = scrapy.Field()
    info_title = scrapy.Field()       # <p> 段落拼接
    info_content = scrapy.Field()     # <h3> 区段拼接
    price = scrapy.Field()
    cover_url = scrapy.Field()
    publish_date = scrapy.Field()


class WorkFileItem(scrapy.Item):
    file_id = scrapy.Field()
    album_id = scrapy.Field()
    file_name = scrapy.Field()
    object_key = scrapy.Field()
    file_type = scrapy.Field()        # 全部 "preview"
    track_length = scrapy.Field()
    file_size = scrapy.Field()
    sort_order = scrapy.Field()


class CircleItem(scrapy.Item):
    circle_id = scrapy.Field()
    dizzylab_labelid = scrapy.Field()    # 去重键
    name = scrapy.Field()
    description = scrapy.Field()
    logo_url = scrapy.Field()
    owner_user_id = scrapy.Field()       # 留空


class AlbumCircleItem(scrapy.Item):
    album_id = scrapy.Field()
    circle_id = scrapy.Field()


class TagItem(scrapy.Item):
    tag_id = scrapy.Field()
    name = scrapy.Field()                # strip("#") 之后的值


class AlbumTagItem(scrapy.Item):
    album_id = scrapy.Field()
    tag_id = scrapy.Field()


class UserItem(scrapy.Item):
    user_id = scrapy.Field()
    dizzylab_user_id = scrapy.Field()    # 去重键
    username = scrapy.Field()
    avatar_url = scrapy.Field()
    user_role = scrapy.Field()           # 默认 "normal"


class UserCircleItem(scrapy.Item):
    user_id = scrapy.Field()
    circle_id = scrapy.Field()


class CommentItem(scrapy.Item):
    comment_id = scrapy.Field()
    user_id = scrapy.Field()
    album_id = scrapy.Field()
    content = scrapy.Field()
    created_at = scrapy.Field()


class OwnedAlbumItem(scrapy.Item):
    user_id = scrapy.Field()
    album_id = scrapy.Field()
    created_at = scrapy.Field()


class FavoriteItem(scrapy.Item):
    user_id = scrapy.Field()
    album_id = scrapy.Field()
    created_at = scrapy.Field()


class CircleFollowItem(scrapy.Item):
    user_id = scrapy.Field()
    circle_id = scrapy.Field()
    created_at = scrapy.Field()


class UserFollowItem(scrapy.Item):
    user_id = scrapy.Field()
    followed_user_id = scrapy.Field()
    created_at = scrapy.Field()
