<template>
  <div class="home-page">
    <!-- Hero 区域 -->
    <section class="hero">
      <div class="hero-content container-wide">
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="wave-icon">🎵</span>
            发现独立电子音乐
          </h1>
          <p class="hero-subtitle">
            探索来自世界各地创作者的声音，从东方同人到硬核电子，免费试听，支持你爱的音乐人。
          </p>
          <div class="hero-actions">
            <router-link to="/tag" class="hero-btn primary">浏览全部</router-link>
            <button class="hero-btn secondary" @click="scrollToLatest">最新专辑 ↓</button>
          </div>
        </div>
        <div class="hero-stats">
          <div class="stat">
            <span class="stat-number">{{ totalAlbums }}+</span>
            <span class="stat-label">张专辑</span>
          </div>
          <div class="stat">
            <span class="stat-number">{{ circlesCount }}</span>
            <span class="stat-label">个社团</span>
          </div>
          <div class="stat">
            <span class="stat-number">100%</span>
            <span class="stat-label">免费试听</span>
          </div>
        </div>
      </div>
      <div class="hero-wave"></div>
    </section>

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
import { fetchAlbums, fetchCircles, fetchAlbum } from '../api/mock.js';
import { usePlayerStore } from '../stores/player.js';

export default {
  name: 'HomeView',
  components: { AlbumGrid },
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

/* Hero 区域 */
.hero {
  position: relative;
  background: linear-gradient(135deg, #0e0e0e 0%, #1a1a1a 100%);
  border-bottom: 1px solid var(--color-border);
  padding: 4rem 0 5rem;
  overflow: hidden;
}

.hero-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-text {
  flex: 1;
  min-width: 280px;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1.2;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.wave-icon {
  display: inline-block;
  margin-right: 12px;
  filter: drop-shadow(0 0 6px var(--color-accent));
}

.hero-subtitle {
  font-size: 1.1rem;
  color: var(--color-text-muted);
  max-width: 500px;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.hero-btn {
  padding: 0.8rem 2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
  border: none;
  font-size: 0.9rem;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.hero-btn.primary {
  background: var(--color-accent);
  color: var(--color-bg-primary);
}

.hero-btn.primary:hover {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
}

.hero-btn.secondary {
  background: transparent;
  border: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
}

.hero-btn.secondary:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  transform: translateY(-2px);
}

.hero-stats {
  display: flex;
  gap: 2rem;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(8px);
  padding: 1.5rem 2rem;
  border: 1px solid var(--color-border);
  flex-shrink: 0;
}

.stat {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-accent);
  line-height: 1;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--color-text-dim);
  margin-top: 0.3rem;
}

.hero-wave {
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 40px;
  background: repeating-linear-gradient(45deg, var(--color-accent) 0px, var(--color-accent) 2px, transparent 2px, transparent 8px);
  opacity: 0.2;
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
  .hero {
    padding: 3rem 0 4rem;
  }
  .hero-title {
    font-size: 2rem;
  }
  .hero-content {
    flex-direction: column;
    text-align: center;
  }
  .hero-stats {
    width: 100%;
    justify-content: center;
  }
  .section-title {
    font-size: 1.4rem;
  }
  .circle-card-horizontal {
    flex: 0 0 220px;
  }
}
</style>