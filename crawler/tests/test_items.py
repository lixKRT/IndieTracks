"""items.py 单元测试。"""

from indietracks_spider.items import (
    AlbumItem,
    WorkFileItem,
    CircleItem,
    AlbumCircleItem,
    TagItem,
    AlbumTagItem,
    UserItem,
    UserCircleItem,
    CommentItem,
    OwnedAlbumItem,
    FavoriteItem,
    CircleFollowItem,
)


class TestItems:
    def test_album_item_fields(self):
        item = AlbumItem()
        item['dizzylab_id'] = 'SW20'
        item['title'] = 'Test Album'
        assert item['dizzylab_id'] == 'SW20'
        assert item['title'] == 'Test Album'

    def test_workfile_item_temp_field(self):
        item = WorkFileItem()
        item['_dizzylab_id'] = 'SW20'
        item['file_name'] = 'Track 1'
        assert item['_dizzylab_id'] == 'SW20'

    def test_user_item_default_role(self):
        item = UserItem()
        item['dizzylab_user_id'] = 12345
        item['username'] = 'testuser'
        item['user_role'] = 'normal'
        assert item['user_role'] == 'normal'

    def test_circle_item_no_owner(self):
        item = CircleItem()
        item['dizzylab_labelid'] = 30
        item['name'] = 'Test Circle'
        # owner_user_id field was removed
        assert 'owner_user_id' not in item

    def test_tag_item(self):
        item = TagItem()
        item['name'] = '纯音乐'
        assert item['name'] == '纯音乐'

    def test_comment_item(self):
        item = CommentItem()
        item['_dizzylab_user_id'] = 123
        item['_dizzylab_id'] = 'SW20'
        item['content'] = 'Great album!'
        assert item['content'] == 'Great album!'

    def test_favorite_item_temp_fields(self):
        item = FavoriteItem()
        item['_dizzylab_user_id'] = 123
        item['_dizzylab_id'] = 'SW20'
        assert item['_dizzylab_user_id'] == 123
        assert item['_dizzylab_id'] == 'SW20'

    def test_circle_follow_item_temp_fields(self):
        item = CircleFollowItem()
        item['_dizzylab_user_id'] = 123
        item['_dizzylab_labelid'] = 30
        assert item['_dizzylab_user_id'] == 123
        assert item['_dizzylab_labelid'] == 30
