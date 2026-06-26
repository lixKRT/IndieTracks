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
      :favorited-ids="favorite.favoriteAlbumIds"
      @album-click="goToAlbum"
      @circle-click="goToCircle"
      @tag-click="onTagChange"
      @preview="handlePreview"
      @toggle-favorite="handleToggleFavorite"
    />
  </div>
</template>

<script>
import AlbumGrid from '../components/organisms/AlbumGrid.vue';
import TagFilter from '../components/organisms/TagFilter.vue';
import { fetchAlbums, getTags } from '../api';
import { useFavoriteStore } from '../stores/favorite.js';
import { useNavigation } from '../composables/navigation.js';
import { useAuthGuard } from '../composables/authGuard.js';
import { usePreviewPlay } from '../composables/previewPlay.js';

export default {
  name: 'TagBrowseView',
  components: { AlbumGrid, TagFilter },
  data() {
    return {
      allTags: [],
      filterTag: '',
      filterPrice: '',
      albums: [],
      loading: true
    };
  },
  setup() {
    const favorite = useFavoriteStore();
    const { goToAlbum, goToCircle } = useNavigation();
    const { guard } = useAuthGuard();
    const { playPreview } = usePreviewPlay();
    return { favorite, goToAlbum, goToCircle, guard, playPreview };
  },
  watch: {
    // 筛选条件变化时重新加载；同时监听路由 query 以支持浏览器前进/后退
    filterTag() { this.loadAlbums(); },
    filterPrice() { this.loadAlbums(); },
    '$route.query'() { this.syncFromQuery(); }
  },
  async mounted() {
    this.allTags = await getTags();
    this.syncFromQuery();
  },
  methods: {
    // 从 URL query 同步筛选状态，使筛选结果可通过 URL 分享
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
      this.$router.replace({ query: { ...this.$route.query, tag: tag || undefined } }); // replace 不产生历史记录
    },
    onPriceChange(price) {
      this.filterPrice = price;
      this.$router.replace({ query: { ...this.$route.query, price: price || undefined } });
    },
    async handlePreview(album) {
      await this.playPreview(album.album_id);
    },
    handleToggleFavorite(album) {
      this.guard(() => this.favorite.toggleFavorite(album.album_id));
    }
  }
};
</script>

<style scoped>
.tag-page { padding-top: var(--spacing-xl); }
.page-title { font-size: 1.8rem; color: var(--color-text-primary); margin-bottom: var(--spacing-xl); }
</style>
