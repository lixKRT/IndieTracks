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

      <!-- 专辑列表 -->
      <section v-if="circle.albums.length > 0" class="detail-section">
        <h2 class="section-title">
          <i class="fas fa-music"></i> 专辑作品
        </h2>
        <div class="album-list">
          <div
            v-for="a in circle.albums"
            :key="a.album_id"
            class="album-row"
          >
            <div class="album-cover" @click="$router.push(`/album/${a.album_id}`)">
              <img :src="a.cover_url" :alt="a.title">
            </div>
            <div class="album-info" @click="$router.push(`/album/${a.album_id}`)">
              <div class="album-title">{{ a.title }}</div>
              <div class="album-meta">{{ a.track_count }} 首 · {{ a.tags.slice(0, 3).join(' · ') }}</div>
            </div>
            <div class="album-actions">
              <button class="album-play-btn" @click.stop="addToPlaylist(a)" title="添加到播放列表">
                <i class="fas fa-play"></i>
              </button>
              <span v-if="a.price > 0" class="album-price">¥{{ a.price }}</span>
              <span v-else class="album-price free">免费</span>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script>
import { fetchCircle, fetchAlbum } from '../api/mock.js';
import { usePlayerStore } from '../stores/player.js';

export default {
  name: 'LabelDetailView',
  data() {
    return { circle: null, loading: true };
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
    async addToPlaylist(album) {
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

/* 专辑列表 */
.album-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.album-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  padding: var(--spacing-md);
  transition: all 0.2s ease;
}

.album-row:hover {
  background: var(--color-bg-secondary);
  border-color: var(--color-accent);
  transform: translateX(4px);
}

.album-cover {
  flex-shrink: 0;
  width: 60px;
  height: 60px;
  cursor: pointer;
  overflow: hidden;
}

.album-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s;
}

.album-cover:hover img {
  transform: scale(1.05);
}

.album-info {
  flex: 1;
  cursor: pointer;
  min-width: 0;
}

.album-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.album-meta {
  font-size: 0.75rem;
  color: var(--color-text-dim);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.album-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex-shrink: 0;
}

.album-play-btn {
  background: none;
  border: 1px solid var(--color-border-light);
  color: var(--color-text-muted);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.album-play-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: rgba(255,107,107,0.1);
}

.album-price {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-accent);
}

.album-price.free {
  color: #4caf50;
}

/* 响应式 */
@media (max-width: 768px) {
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
  .album-row {
    flex-wrap: wrap;
  }
  .album-actions {
    margin-left: auto;
  }
}
</style>