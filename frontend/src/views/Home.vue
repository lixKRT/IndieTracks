<!-- 首页 — 作品列表 -->
<template>
  <AlbumGrid
    :albums="albums"
    :loading="loading"
    :showAll="showAll"
    :maxVisible="maxVisible"
    @album-click="goToAlbum"
    @circle-click="goToCircle"
    @tag-click="filterByTag"
    @preview="handlePreview"
    @view-all="showAll = true"
  />
</template>

<script>
import AlbumGrid from '../components/organisms/AlbumGrid.vue';
import { fetchAlbums, fetchAlbum } from '../api/mock.js';
import { usePlayerStore } from '../stores/player.js';

export default {
  name: 'HomeView',
  components: { AlbumGrid },
  data() {
    return {
      albums: [],
      loading: true,
      showAll: false,
      maxVisible: 6
    };
  },
  async mounted() {
    try {
      const result = await fetchAlbums({ page_size: 48 });
      this.albums = result.data;
    } catch (e) {
      console.error('加载专辑列表失败:', e);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    goToAlbum(album) {
      this.$router.push(`/album/${album.album_id}`);
    },
    goToCircle(album) {
      this.$router.push(`/label/${album.circle_id}`);
    },
    filterByTag(tag) {
      this.$router.push({ path: '/tag', query: { tag } });
    },
    handlePreview(album) {
      fetchAlbum(album.album_id).then(detail => {
        const player = usePlayerStore();
        player.addAlbumTracks(detail.tracks, 0);
      });
    }
  }
};
</script>
