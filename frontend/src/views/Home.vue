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
        :loadingMore="loadingMore"
        :hasMore="albums.length < totalAlbums"
        :favorited-ids="favorite.favoriteAlbumIds"
        :cart-ids="cartIds"
        @album-click="goToAlbum"
        @circle-click="goToCircle"
        @tag-click="goToTag"
        @preview="handlePreview"
        @toggle-favorite="handleToggleFavorite"
        @toggle-cart="handleToggleCart"
        @load-more="loadMore"
      />
    </section>

    <!-- 推荐社团横向滚动区 -->
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
          @click="goToCircleById(circle.circle_id)"
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
import { fetchAlbums, fetchCircles, getCart, addToCart, removeFromCart } from '../api';
import { usePlayerStore } from '../stores/player.js';
import { useFavoriteStore } from '../stores/favorite.js';
import { useUserStore } from '../stores/user.js';
import { useNavigation } from '../composables/navigation.js';
import { useAuthGuard } from '../composables/authGuard.js';
import { usePreviewPlay } from '../composables/previewPlay.js';

export default {
  name: 'HomeView',
  components: { AlbumGrid, HeroSection },
  data() {
    return {
      albums: [],
      loading: true,
      loadingMore: false,
      page: 1,
      pageSize: 12,
      totalAlbums: 0,
      featuredCircles: [],
      circlesCount: 0,
      displayAlbums: 0,
      displayCircles: 0,
      cartIds: []
    };
  },
  computed: {
    heroStats() {
      return [
        { value: `${this.displayAlbums}+`, label: '张专辑' },
        { value: this.displayCircles, label: '个社团' },
        { value: '100%', label: '免费试听' }
      ];
    }
  },
  setup() {
    const player = usePlayerStore();
    const favorite = useFavoriteStore();
    const userStore = useUserStore();
    const { goToAlbum, goToCircle, goToTag, goToCircleById } = useNavigation();
    const { guard } = useAuthGuard();
    const { addPreview } = usePreviewPlay();
    return { player, favorite, userStore, goToAlbum, goToCircle, goToTag, goToCircleById, guard, addPreview };
  },
  async mounted() {
    await this.loadData();
  },
  methods: {
    async loadData() {
      this.loading = true;
      try {
        const albumResult = await fetchAlbums({ page: 1, page_size: this.pageSize });
        this.albums = albumResult.data;
        this.totalAlbums = albumResult.total;
        this.page = 1;

        const circleResult = await fetchCircles();
        this.featuredCircles = circleResult.data.slice(0, 4);
        this.circlesCount = circleResult.data.length;

        // 加载购物车状态
        if (this.userStore.isLoggedIn) {
          try {
            const cartResult = await getCart();
            this.cartIds = (cartResult || []).map(item => item.album_id);
          } catch { /* ignore */ }
        }

        this.animateCount('displayAlbums', this.totalAlbums, 1200);
        this.animateCount('displayCircles', this.circlesCount, 1000);
      } catch (e) {
        console.error('加载首页数据失败:', e);
      } finally {
        this.loading = false;
      }
    },
    animateCount(field, target, duration) {
      const start = performance.now();
      const step = (now) => {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        this[field] = Math.round(ease * target);
        if (progress < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    },
    async loadMore() {
      if (this.loadingMore || this.albums.length >= this.totalAlbums) return;
      this.loadingMore = true;
      try {
        this.page++;
        const result = await fetchAlbums({ page: this.page, page_size: this.pageSize });
        this.albums.push(...result.data);
      } catch (e) {
        console.error('加载更多失败:', e);
        this.page--;
      } finally {
        this.loadingMore = false;
      }
    },
    async handlePreview(album) {
      await this.addPreview(album.album_id);
    },
    async handleToggleFavorite(album) {
      await this.guard(
        () => this.favorite.toggleFavorite(album.album_id),
        () => alert('请先登录')
      );
    },
    async handleToggleCart(album) {
      await this.guard(async () => {
        if (this.cartIds.includes(album.album_id)) {
          await removeFromCart(album.album_id);
          this.cartIds = this.cartIds.filter(id => id !== album.album_id);
        } else {
          await addToCart(album.album_id);
          this.cartIds.push(album.album_id);
        }
        // 更新 Navbar 角标
        window.dispatchEvent(new CustomEvent('cart-updated'));
      }, () => alert('请先登录'));
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

@media (max-width: 768px) {
  .section-title {
    font-size: 1.4rem;
  }
  .circle-card-horizontal {
    flex: 0 0 220px;
  }
}
</style>
