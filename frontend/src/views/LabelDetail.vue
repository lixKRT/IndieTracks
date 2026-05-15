<!-- 社团详情页 -->
<template>
  <div class="label-detail container">
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <template v-else-if="circle">
      <div class="detail-header">
        <img :src="circle.logo_url" :alt="circle.name" class="detail-logo">
        <div class="detail-info">
          <h1 class="detail-name">{{ circle.name }}</h1>
          <p class="detail-desc">{{ circle.description }}</p>
          <div class="detail-stats">
            <span>{{ circle.albums.length }} 张专辑</span>
            <span>{{ circle.members.length }} 名成员</span>
          </div>
        </div>
      </div>

      <!-- 成员列表 -->
      <section v-if="circle.members.length > 0" class="detail-section">
        <h2 class="section-title">成员</h2>
        <div class="member-list">
          <div v-for="m in circle.members" :key="m.user_id" class="member-item">
            <img :src="m.avatar_url" :alt="m.username" class="member-avatar">
            <span class="member-name">{{ m.username }}</span>
            <span class="member-role">{{ m.user_role === 'pro' ? '社团成员' : '普通用户' }}</span>
          </div>
        </div>
      </section>

      <!-- 专辑列表 -->
      <section v-if="circle.albums.length > 0" class="detail-section">
        <h2 class="section-title">发布的专辑</h2>
        <div class="album-list">
          <div
            v-for="a in circle.albums"
            :key="a.album_id"
            class="album-row"
          >
            <img :src="a.cover_url" :alt="a.title" class="album-row-cover" @click="$router.push(`/album/${a.album_id}`)">
            <div class="album-row-info" @click="$router.push(`/album/${a.album_id}`)">
              <span class="album-row-title">{{ a.title }}</span>
              <span class="album-row-meta">{{ a.track_count }} 曲 · {{ a.tags.join(', ') }}</span>
            </div>
            <button class="album-row-play" @click.stop="playAlbum(a)" title="试听"><i class="fas fa-play"></i></button>
            <span v-if="a.price > 0" class="album-row-price">&yen;{{ a.price }}</span>
            <span v-else class="album-row-price free">免费</span>
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
    async playAlbum(album) {
      try {
        const detail = await fetchAlbum(album.album_id);
        const player = usePlayerStore();
        player.playAlbumTracks(detail.tracks, 0);
      } catch (e) {
        console.error('加载专辑曲目失败:', e);
      }
    }
  }
};
</script>

<style scoped>
.label-detail { padding-top: var(--spacing-xl); }

.detail-header { display: flex; gap: var(--spacing-xl); margin-bottom: var(--spacing-xl); }
.detail-logo { width: 120px; height: 120px; object-fit: cover; flex-shrink: 0; }
.detail-info { flex: 1; }
.detail-name { font-size: 1.6rem; color: var(--color-text-primary); margin-bottom: var(--spacing-sm); }
.detail-desc { font-size: 0.9rem; color: var(--color-text-muted); line-height: 1.6; margin-bottom: var(--spacing-sm); }
.detail-stats { display: flex; gap: var(--spacing-xl); font-size: 0.85rem; color: var(--color-text-dim); }

.detail-section { margin-top: var(--spacing-xl); }
.section-title { font-size: 1.2rem; color: var(--color-text-primary); margin-bottom: var(--spacing-md); border-bottom: 1px solid var(--color-border); padding-bottom: var(--spacing-sm); }

.member-list { display: flex; flex-wrap: wrap; gap: var(--spacing-md); }
.member-item { display: flex; align-items: center; gap: var(--spacing-sm); background: var(--color-bg-secondary); padding: var(--spacing-sm) var(--spacing-md); border: 1px solid var(--color-border); }
.member-avatar { width: 36px; height: 36px; object-fit: cover; }
.member-name { font-size: 0.85rem; color: var(--color-text-primary); }
.member-role { font-size: 0.7rem; color: var(--color-text-dim); margin-left: auto; }

.album-list { display: flex; flex-direction: column; gap: 1px; background: var(--color-border); }
.album-row { display: flex; align-items: center; gap: var(--spacing-md); padding: var(--spacing-sm) var(--spacing-md); background: var(--color-bg-primary); cursor: pointer; transition: background var(--transition-fast); }
.album-row:hover { background: var(--color-bg-secondary); }
.album-row-cover { width: 48px; height: 48px; object-fit: cover; flex-shrink: 0; }
.album-row-info { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.album-row-title { font-size: 0.85rem; color: var(--color-text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.album-row-meta { font-size: 0.75rem; color: var(--color-text-dim); }
.album-row-play {
  flex-shrink: 0;
  background: none; border: 1px solid var(--color-border);
  color: var(--color-text-muted); width: 30px; height: 30px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 0.7rem;
  transition: all var(--transition-fast);
  margin-right: var(--spacing-sm);
  opacity: 0;
}
.album-row:hover .album-row-play { opacity: 1; }
.album-row-play:hover { border-color: var(--color-accent); color: var(--color-accent); }
.album-row-price { font-size: 0.9rem; font-weight: 600; color: var(--color-accent); flex-shrink: 0; }
.album-row-price.free { color: #4CAF50; }
</style>
