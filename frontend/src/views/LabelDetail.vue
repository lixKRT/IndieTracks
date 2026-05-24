<template>
  <div class="label-detail container-wide">
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <template v-else-if="circle">
      <!-- 社团头部 Hero -->
      <div class="detail-hero">
        <div class="detail-header">
          <div class="detail-logo-wrapper">
            <img :src="circle.logo_url" :alt="circle.name" class="detail-logo">
          </div>
          <div class="detail-info">
            <h1 class="detail-name">{{ circle.name }}</h1>
            <p class="detail-desc">{{ circle.description }}</p>
            <div class="detail-stats">
              <span><i class="fas fa-compact-disc"></i> {{ circle.albums.length }} 张专辑</span>
              <span><i class="fas fa-user-friends"></i> {{ circle.members.length }} 名成员</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 成员列表 -->
      <section v-if="circle.members.length > 0" class="detail-section">
        <h2 class="section-title">
          <i class="fas fa-users"></i> 成员
        </h2>
        <div class="member-list">
          <div v-for="m in circle.members" :key="m.user_id" class="member-item">
            <img :src="m.avatar_url" :alt="m.username" class="member-avatar">
            <div class="member-info">
              <span class="member-name">{{ m.username }}</span>
              <span class="member-role">{{ m.user_role === 'pro' ? '创作者' : '听众' }}</span>
            </div>
          </div>
        </div>
      </section>

      <section v-if="circle.albums.length > 0" class="detail-section">
        <h2 class="section-title">
          <i class="fas fa-music"></i> 专辑作品
        </h2>
        <div class="albums-grid">
          <AlbumCard
            v-for="album in enhancedAlbums"
            :key="album.album_id"
            :album="album"
            @album-click="goToAlbum"
            @circle-click="goToCircleFromAlbum"
            @tag-click="goToTag"
            @preview="handlePreview"
          />
        </div>
      </section>
    </template>
  </div>
</template>

<script>
import { fetchCircle, fetchAlbum } from '../api/mock.js';
import { usePlayerStore } from '../stores/player.js';
import AlbumCard from '../components/molecules/AlbumCard.vue';

export default {
  name: 'LabelDetailView',
  components: { AlbumCard },
  data() {
    return { circle: null, loading: true };
  },
  computed: {
    // 为每个专辑添加 circle_logo_url 字段，以匹配 AlbumCard 所需的数据结构
    enhancedAlbums() {
      if (!this.circle) return [];
      return this.circle.albums.map(album => ({
        ...album,
        circle_logo_url: this.circle.logo_url  // 补充社团Logo
      }));
    }
  },
  async mounted() {
    try {
      const id = this.$route.params.id;
      this.circle = await fetchCircle(id);
    } catch (e) {
      console.error('加载社团详情失败:', e);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    goToAlbum(album) {
      this.$router.push(`/album/${album.album_id}`);
    },
    goToCircleFromAlbum(album) {
      this.$router.push(`/label/${album.circle_id}`);
    },
    goToTag(tag) {
      this.$router.push({ path: '/tag', query: { tag } });
    },
    async handlePreview(album) {
      try {
        const detail = await fetchAlbum(album.album_id);
        const player = usePlayerStore();
        player.addAlbumTracks(detail.tracks, 0);
      } catch (e) {
        console.error('加载专辑曲目失败:', e);
      }
    }
  }
};
</script>

<style scoped>
.label-detail {
  padding-top: var(--spacing-xl);
  padding-bottom: var(--spacing-2xl);
}

/* Hero 区域 */
.detail-hero {
  background: linear-gradient(135deg, rgba(20,20,20,0.9) 0%, rgba(10,10,10,0.95) 100%);
  border: 1px solid var(--color-border);
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-xl);
}

.detail-header {
  display: flex;
  gap: var(--spacing-xl);
  align-items: center;
  flex-wrap: wrap;
}

.detail-logo-wrapper {
  flex-shrink: 0;
  width: 140px;
  height: 140px;
  overflow: hidden;
  border: 2px solid var(--color-border);
  transition: transform 0.3s;
}

.detail-logo-wrapper:hover {
  transform: scale(1.02);
  border-color: var(--color-accent);
}

.detail-logo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-info {
  flex: 1;
  min-width: 200px;
}

.detail-name {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
  letter-spacing: -0.3px;
}

.detail-desc {
  font-size: 0.95rem;
  color: var(--color-text-muted);
  line-height: 1.6;
  margin-bottom: var(--spacing-md);
}

.detail-stats {
  display: flex;
  gap: var(--spacing-lg);
  font-size: 0.85rem;
  color: var(--color-text-dim);
}

.detail-stats i {
  margin-right: 6px;
  width: 16px;
  color: var(--color-accent);
}

/* 公用 section */
.detail-section {
  margin-top: var(--spacing-xl);
}

.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
  border-left: 4px solid var(--color-accent);
  padding-left: var(--spacing-md);
}

.section-title i {
  margin-right: 8px;
  color: var(--color-accent);
}

/* 成员列表 */
.member-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.member-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  background: var(--color-bg-secondary);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  transition: background 0.2s, border-color 0.2s;
}

.member-item:hover {
  background: var(--color-bg-tertiary);
  border-color: var(--color-accent);
}

.member-avatar {
  width: 48px;
  height: 48px;
  object-fit: cover;
  flex-shrink: 0;
}

.member-info {
  flex: 1;
}

.member-name {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.member-role {
  font-size: 0.7rem;
  color: var(--color-text-dim);
}


.albums-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-xl);
}


@media (max-width: 768px) {
  .albums-grid {
    grid-template-columns: 1fr;
  }
  .detail-header {
    flex-direction: column;
    text-align: center;
  }
  .detail-logo-wrapper {
    width: 100px;
    height: 100px;
  }
  .detail-stats {
    justify-content: center;
  }
}
</style>