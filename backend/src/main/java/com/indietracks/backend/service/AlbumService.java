package com.indietracks.backend.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.indietracks.backend.dto.AlbumDetail;
import com.indietracks.backend.dto.AlbumListItem;
import com.indietracks.backend.entity.Album;
import com.indietracks.backend.mapper.AlbumMapper;
import com.indietracks.backend.util.UrlPresignHelper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class AlbumService {

    private final AlbumMapper albumMapper;
    private final UrlPresignHelper urlPresign;

    public AlbumService(AlbumMapper albumMapper, UrlPresignHelper urlPresign) {
        this.albumMapper = albumMapper;
        this.urlPresign = urlPresign;
    }

    public IPage<AlbumListItem> getAlbumList(int page, int pageSize, String tag, String search, String price, String sort) {
        Page<AlbumListItem> pageParam = new Page<>(page, pageSize);
        IPage<AlbumListItem> result = albumMapper.selectAlbumList(pageParam, tag, search, price, sort);
        urlPresign.presignAlbumList(result.getRecords());
        return result;
    }

    public AlbumDetail getAlbumDetail(Integer albumId) {
        Album album = albumMapper.selectById(albumId);
        if (album == null) return null;

        AlbumDetail detail = new AlbumDetail();
        detail.setAlbum_id(album.getAlbum_id());
        detail.setTitle(album.getTitle());
        detail.setCover_url(album.getCover_url());
        detail.setPrice(album.getPrice());
        detail.setPublish_date(album.getPublish_date());
        detail.setInfo_title(album.getInfo_title());
        detail.setInfo_content(album.getInfo_content());

        // 社团信息
        AlbumDetail.AlbumCircleInfo circle = albumMapper.selectCircleByAlbumId(albumId);
        detail.setCircle(circle);

        // 标签
        detail.setTags(albumMapper.selectTagsByAlbumId(albumId));

        // 曲目 + 预签名 URL
        List<AlbumDetail.TrackInfo> tracks = albumMapper.selectTracksByAlbumId(albumId);
        for (AlbumDetail.TrackInfo track : tracks) {
            track.setPreview_url(getObjectKeyFromTrack(track, album));
        }
        detail.setTracks(tracks);

        // 评论（首页 5 条）
        List<AlbumDetail.CommentInfo> comments = albumMapper.selectCommentsPage(albumId, 5, 0);
        detail.setComments(comments);

        // 统一预签名
        urlPresign.presignAlbumDetail(detail);
        urlPresign.presignTracks(detail.getTracks());

        return detail;
    }

    public List<AlbumListItem> getRandomRecommendations(Integer albumId, int limit) {
        List<AlbumListItem> results = albumMapper.selectRandomAlbums(albumId, limit);
        urlPresign.presignAlbumList(results);
        return results;
    }

    private String getObjectKeyFromTrack(AlbumDetail.TrackInfo track, Album album) {
        if (track.getFile_type() == null) return null;
        String prefix = "preview".equals(track.getFile_type()) ? "audio/preview/" : "audio/full/";
        String slug = album.getDizzylab_id();
        String filename = String.format("%03d.mp3", track.getSort_order());
        return prefix + slug + "/" + filename;
    }
}
