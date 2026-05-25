<!-- 分类浏览页 -->
<template>
  <div class="tag-page container-wide">
    <h1 class="page-title">标签</h1>

    <TagFilter
      :tags="allTags"
      :selectedTag="filterTag"
      :selectedPrice="filterPrice"
      @update:tag="onTagChange"
      @update:price="onPriceChange"
    />

    <AlbumGrid
      :albums="albums"
      :loading="loading"
      :showAll="true"
      :maxVisible="48"
      @album-click="goToAlbum"
      @circle-click="goToCircle"
      @tag-click="onTagChange"
      @preview="handlePreview"
    />
  </div>
</template>

<script>
import AlbumGrid from '../components/organisms/AlbumGrid.vue';
import TagFilter from '../components/organisms/TagFilter.vue';
import { fetchAlbums, getTags, fetchAlbum } from '../api/mock.js';
import { usePlayerStore } from '../stores/player.js';

export default {
  name: 'TagBrowseView',
  components: { AlbumGrid, TagFilter },
  data() {
    return {
      allTags: getTags(),
      filterTag: '',
      filterPrice: '',
      albums: [],
      loading: true
    };
  },
  watch: {
    filterTag() { this.loadAlbums(); },
    filterPrice() { this.loadAlbums(); },
    '$route.query'() { this.syncFromQuery(); }
  },
  async mounted() {
    this.syncFromQuery();
  },
  methods: {
    syncFromQuery() {
      const q = this.$route.query;
      if (q.tag !== undefined) this.filterTag = q.tag || '';
      if (q.price !== undefined) this.filterPrice = q.price || '';
      if (q.search !== undefined) this.searchQuery = q.search || '';
      this.loadAlbums();
    },
    async loadAlbums() {
      this.loading = true;
      try {
        const params = { page_size: 48 };
        if (this.filterTag) params.tag = this.filterTag;
        if (this.filterPrice) params.price = this.filterPrice;
        if (this.searchQuery) params.search = this.searchQuery;
        const result = await fetchAlbums(params);
        this.albums = result.data;
      } catch (e) {
        console.error('加载专辑失败:', e);
      } finally {
        this.loading = false;
      }
    },
    onTagChange(tag) {
      this.filterTag = tag;
      this.$router.replace({ query: { ...this.$route.query, tag: tag || undefined } });
    },
    onPriceChange(price) {
      this.filterPrice = price;
      this.$router.replace({ query: { ...this.$route.query, price: price || undefined } });
    },
    goToAlbum(album) { this.$router.push(`/album/${album.album_id}`); },
    goToCircle(album) { this.$router.push(`/label/${album.circle_id}`); },
    handlePreview(album) {
      fetchAlbum(album.album_id).then(detail => {
        const player = usePlayerStore();
        player.playAlbumTracks(detail.tracks, 0);
      });
    }
  }
};
</script>

<style scoped>
.tag-page { padding-top: var(--spacing-xl); }
.page-title { font-size: 1.8rem; color: var(--color-text-primary); margin-bottom: var(--spacing-xl); }
</style>
