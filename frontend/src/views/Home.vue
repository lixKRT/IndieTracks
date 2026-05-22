<template>
  <div class="home-page">
    <!-- Hero 区域 -->
    <HeroSection
      :stats="heroStats"
      @secondary-action-click="scrollToLatest"
    />

    <!-- 最新专辑区域 -->
    <section class="latest-section container-wide" ref="latestSection">
      <div class="section-header">
        <div>
          <h2 class="section-title">最新发行</h2>
          <p class="section-subtitle">近期上架的优质作品</p>
        </div>
        <router-link to="/tag" class="section-more">查看全部 →</router-link>
      </div>

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
    </section>

    <!-- 推荐社团横向滚动区（可选） -->
    <section class="featured-circles container-wide" v-if="featuredCircles.length">
      <div class="section-header">
        <div>
          <h2 class="section-title">热门社团</h2>
          <p class="section-subtitle">发现更多优质厂牌</p>
        </div>
        <router-link to="/labels" class="section-more">所有社团 →</router-link>
      </div>
      <div class="circles-scroll">
        <div
          v-for="circle in featuredCircles"
          :key="circle.circle_id"
          class="circle-card-horizontal"
          @click="goToCircleDetail(circle)"
        >
          <div class="circle-avatar">
            <img :src="circle.logo_url" :alt="circle.name">
          </div>
          <div class="circle-info">
            <h4>{{ circle.name }}</h4>
            <span>{{ circle.album_count }} 张专辑</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import AlbumGrid from '../components/organisms/AlbumGrid.vue';
import HeroSection from '../components/organisms/HeroSection.vue';
import { fetchAlbums, fetchCircles, fetchAlbum } from '../api/mock.js';
import { usePlayerStore } from '../stores/player.js';

export default {
  name: 'HomeView',
  components: { AlbumGrid, HeroSection },
  data() {
    return {
      albums: [],
      loading: true,
      showAll: false,
      maxVisible: 6,
      totalAlbums: 0,
      featuredCircles: [],
      circlesCount: 0
    };
  },
  computed: {
    heroStats() {
      return [
        { value: `${this.totalAlbums}+`, label: '张专辑' },
        { value: this.circlesCount, label: '个社团' },
        { value: '100%', label: '免费试听' }
      ];
    }
  },
  async mounted() {
    await this.loadData();
  },
  methods: {
    async loadData() {
      this.loading = true;
      try {
        // 加载专辑列表（取前12张用于最新区域）
        const albumResult = await fetchAlbums({ page_size: 12 });
        this.albums = albumResult.data;
        this.totalAlbums = albumResult.total;

        // 加载社团列表（用于热门社团展示）
        const circleResult = await fetchCircles();
        this.featuredCircles = circleResult.data.slice(0, 4);
        this.circlesCount = circleResult.data.length;
      } catch (e) {
        console.error('加载首页数据失败:', e);
      } finally {
        this.loading = false;
      }
    },
    goToAlbum(album) {
      this.$router.push(`/album/${album.album_id}`);
    },
    goToCircle(album) {
      this.$router.push(`/label/${album.circle_id}`);
    },
    goToCircleDetail(circle) {
      this.$router.push(`/label/${circle.circle_id}`);
    },
    filterByTag(tag) {
      this.$router.push({ path: '/tag', query: { tag } });
    },
    handlePreview(album) {
      fetchAlbum(album.album_id).then(detail => {
        const player = usePlayerStore();
        player.addAlbumTracks(detail.tracks, 0);
      });
    },
    scrollToLatest() {
      this.$refs.latestSection?.scrollIntoView({ behavior: 'smooth' });
    }
  }
};
</script>

<style scoped>
.home-page {
  background: var(--color-bg-primary);
}

/* 公共区块样式 */
.latest-section,
.featured-circles {
  padding: 3rem 0;
}

.container-wide {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 0.3rem;
}

.section-subtitle {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.section-more {
  color: var(--color-text-dim);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.section-more:hover {
  color: var(--color-accent);
}

/* 横向滚动社团卡片 */
.circles-scroll {
  display: flex;
  gap: 1.5rem;
  overflow-x: auto;
  padding-bottom: 1rem;
  scrollbar-width: thin;
}

.circles-scroll::-webkit-scrollbar {
  height: 4px;
}

.circles-scroll::-webkit-scrollbar-thumb {
  background: var(--color-border);
}

.circle-card-horizontal {
  flex: 0 0 260px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: all 0.25s;
}

.circle-card-horizontal:hover {
  transform: translateY(-4px);
  border-color: var(--color-accent);
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

.circle-avatar {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  background: var(--color-bg-tertiary);
}

.circle-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.circle-info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.circle-info span {
  font-size: 0.7rem;
  color: var(--color-text-dim);
}

/* 响应式 */
@media (max-width: 768px) {
  .section-title {
    font-size: 1.4rem;
  }
  .circle-card-horizontal {
    flex: 0 0 220px;
  }
}
</style>