<!-- 专辑详情页 -->
<template>
  <div class="album-detail container">
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <template v-else-if="album">
      <!-- 封面 + 基本信息 -->
      <div class="detail-header">
        <div class="detail-cover">
          <img :src="album.cover_url" :alt="album.title">
          <span v-if="album.price === 0" class="free-badge">免费</span>
        </div>

        <div class="detail-info">
          <h1 class="detail-title">{{ album.title }}</h1>

          <div class="detail-circle" @click="goToCircle">
            <img :src="album.circle.logo_url" :alt="album.circle.name" class="detail-circle-logo">
            <span>{{ album.circle.name }}</span>
          </div>

          <div class="detail-meta">
            <span>发布于 {{ album.publish_date }}</span>
            <span v-if="album.price > 0" class="detail-price">&yen; {{ album.price }}</span>
            <span v-else class="detail-price free">免费</span>
          </div>

          <div class="detail-tags">
            <span v-for="tag in album.tags" :key="tag.tag_id" class="tag" @click="goToTag(tag.name)">
              #{{ tag.name }}
            </span>
          </div>

          <button class="detail-play-all" @click="playAll">
            <i class="fas fa-play"></i> 试听全部
          </button>
          <button class="detail-buy" v-if="album.price > 0">
            <i class="fas fa-shopping-cart"></i> 购买 &yen;{{ album.price }}
          </button>
        </div>
      </div>

      <!-- 专辑内容信息 -->
      <div v-if="album.info_content" class="detail-content">
        <h2 v-if="album.info_title" class="detail-content-title">{{ album.info_title }}</h2>
        <p class="detail-content-body">{{ album.info_content }}</p>
      </div>

      <!-- 曲目列表 -->
      <TrackList :tracks="album.tracks" @preview="handlePreview" />

      <!-- 评论区 -->
      <CommentSection :comments="localComments" @add-comment="addComment" />
    </template>
  </div>
</template>

<script>
import TrackList from '../components/organisms/TrackList.vue';
import CommentSection from '../components/organisms/CommentSection.vue';
import { fetchAlbum } from '../api/mock.js';
import { usePlayerStore } from '../stores/player.js';

export default {
  name: 'AlbumDetailView',
  components: { TrackList, CommentSection },
  data() {
    return {
      album: null,
      loading: true,
      localComments: []
    };
  },
  async mounted() {
    try {
      const id = this.$route.params.id;
      this.album = await fetchAlbum(id);
      this.localComments = [...(this.album.comments || [])];
    } catch (e) {
      console.error('加载专辑详情失败:', e);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    goToCircle() {
      if (this.album?.circle) {
        this.$router.push(`/label/${this.album.circle.circle_id}`);
      }
    },
    goToTag(name) {
      this.$router.push({ path: '/tag', query: { tag: name } });
    },
    handlePreview(tracks, startIndex) {
      const player = usePlayerStore();
      player.addAlbumTracks(tracks, startIndex);
    },
    playAll() {
      if (this.album?.tracks) {
        const player = usePlayerStore();
        player.addAlbumTracks(this.album.tracks, 0);
      }
    },
    addComment(content) {
      this.localComments.push({
        comment_id: Date.now(),
        username: '匿名用户',
        avatar_url: 'https://placehold.co/64x64/444/fff?text=U',
        content,
        created_at: new Date().toISOString().slice(0, 10)
      });
    }
  }
};
</script>

<style scoped>
.album-detail { padding-top: var(--spacing-xl); }

/* 封面 + 信息 */
.detail-header { display: flex; gap: var(--spacing-xl); margin-bottom: var(--spacing-xl); }
.detail-cover { position: relative; width: 40%; aspect-ratio: 1/1; flex-shrink: 0; }
.detail-cover img { width: 100%; height: 100%; object-fit: cover; display: block; }
.free-badge { position: absolute; top: var(--spacing-sm); left: var(--spacing-sm); background: var(--color-accent); color: var(--color-text-primary); padding: 3px 10px; font-size: 0.8rem; font-weight: 600; }

.detail-info { flex: 1; display: flex; flex-direction: column; gap: var(--spacing-md); }
.detail-title { font-size: 1.6rem; font-weight: 700; color: var(--color-text-primary); }
.detail-circle { display: flex; align-items: center; gap: var(--spacing-sm); cursor: pointer; }
.detail-circle:hover span { color: var(--color-accent); }
.detail-circle-logo { width: 32px; height: 32px; object-fit: cover; flex-shrink: 0; }
.detail-circle span { font-size: 0.95rem; color: var(--color-text-muted); transition: color var(--transition-fast); }

.detail-meta { display: flex; align-items: center; gap: var(--spacing-lg); font-size: 0.85rem; color: var(--color-text-dim); }
.detail-price { font-size: 1.3rem; font-weight: 700; color: var(--color-accent); }
.detail-price.free { color: #4CAF50; }

.detail-tags { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag { font-size: 0.75rem; color: var(--color-text-muted); background: rgba(255,255,255,0.05); padding: 2px 8px; cursor: pointer; transition: color var(--transition-fast); }
.tag:hover { color: var(--color-accent); }

.detail-play-all { align-self: flex-start; background: var(--color-accent); color: var(--color-text-primary); border: none; padding: 0.6rem 1.8rem; font-size: 0.95rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: var(--spacing-sm); transition: background var(--transition-fast); }
.detail-play-all:hover { background: var(--color-accent-hover); }

.detail-buy { align-self: flex-start; background: none; color: var(--color-accent); border: 1px solid var(--color-accent); padding: 0.6rem 1.8rem; font-size: 0.95rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: var(--spacing-sm); transition: all var(--transition-fast); }
.detail-buy:hover { background: var(--color-accent); color: var(--color-text-primary); }

/* 内容信息 */
.detail-content { margin: var(--spacing-xl) 0; padding: var(--spacing-lg); background: var(--color-bg-secondary); border: 1px solid var(--color-border); }
.detail-content-title { font-size: 1.1rem; color: var(--color-text-primary); margin-bottom: var(--spacing-md); }
.detail-content-body { font-size: 0.9rem; color: var(--color-text-muted); line-height: 1.8; white-space: pre-line; }

/* 响应式 */
@media (max-width: 639px) {
  .detail-header { flex-direction: column; }
  .detail-cover { width: 100%; }
}
</style>
