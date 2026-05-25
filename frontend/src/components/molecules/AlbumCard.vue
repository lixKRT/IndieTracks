<!-- 专辑卡片（分子）— 横向布局，桌面 2 列 -->
<template>
  <div class="album-card">
    <div class="card-top">
      <div class="card-cover" @click="$emit('album-click', album)">
        <img :src="album.cover_url" :alt="album.title" class="cover-img">
        <span v-if="album.price === 0" class="free-badge">免费</span>
      </div>

      <div class="card-info">
        <div class="info-circle" @click="$emit('circle-click', album)">
          <img :src="album.circle_logo_url" :alt="album.circle_name" class="circle-logo">
          <span class="circle-name">{{ album.circle_name }}</span>
        </div>
        <p class="info-desc" :title="album.info_title">{{ album.info_title }}</p>
      </div>
    </div>

    <div class="card-bottom">
      <h3 class="album-title" @click="$emit('album-click', album)">{{ album.title }}</h3>
      <div class="bottom-meta-row">
        <div class="album-tags">
          <span v-for="tag in album.tags.slice(0, 3)" :key="tag" class="tag" @click.stop="$emit('tag-click', tag)">#{{ tag }}</span>
          <span v-if="album.tags.length > 3" class="tag tag-more">+{{ album.tags.length - 3 }}</span>
        </div>
        <div class="action-buttons">
          <button 
            class="favorite-btn" 
            :class="{ 'is-favorited': isFavorite }"
            @click.stop="toggleFavorite"
            :title="isFavorite ? '取消收藏' : '收藏'"
          >
            {{ isFavorite ? '★' : '☆' }}
          </button>
          <button class="play-btn" @click="$emit('preview', album)"><i class="fas fa-play"></i> 试听</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useFavoriteStore } from '../../stores/favorite.js';

export default {
  name: 'AlbumCard',
  props: { album: { type: Object, required: true } },
  emits: ['album-click', 'circle-click', 'tag-click', 'preview'],
  data() {
    return {
      favoriteStore: useFavoriteStore()
    };
  },
  computed: {
    isFavorite() {
      return this.favoriteStore.isFavorite(this.album.album_id);
    }
  },
  methods: {
    toggleFavorite() {
      this.favoriteStore.toggleFavorite(this.album.album_id);
    }
  }
};
</script>

<style scoped>
.album-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  overflow: hidden;
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
}

.album-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.card-top { display: flex; }

.card-cover {
  position: relative;
  width: 60%;
  aspect-ratio: 1 / 1;
  flex-shrink: 0;
  cursor: pointer;
  overflow: hidden;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s;
}

.card-cover:hover .cover-img { transform: scale(1.05); }

.free-badge {
  position: absolute;
  top: var(--spacing-sm);
  left: var(--spacing-sm);
  background: var(--color-accent);
  color: var(--color-text-primary);
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: 600;
  z-index: 1;
}

.card-info {
  width: 40%;
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.info-circle {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  margin-bottom: var(--spacing-sm);
  flex-shrink: 0;
}

.circle-logo {
  width: 28px;
  height: 28px;
  object-fit: cover;
  flex-shrink: 0;
}

.circle-name {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color var(--transition-fast);
}

.info-circle:hover .circle-name { color: var(--color-accent); }

.info-desc {
  font-size: 0.75rem;
  color: var(--color-text-dim);
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  flex: 1;
}

.card-bottom {
  padding: var(--spacing-sm) var(--spacing-md) var(--spacing-md);
}

.album-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
  transition: color var(--transition-fast);
  margin-bottom: var(--spacing-sm);
  display: block;
  width: fit-content;
  max-width: 100%;
}

.album-title:hover { color: var(--color-accent); }

.bottom-meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

.favorite-btn {
  background: none;
  border: none;
  color: var(--color-text-muted);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-size: 1.3rem;
}

.favorite-btn:hover { color: #ff6b6b; }
.favorite-btn.is-favorited { color: #ff6b6b; }

.album-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  flex: 1;
  min-width: 0;
}

.tag {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 6px;
  cursor: pointer;
  white-space: nowrap;
  transition: color var(--transition-fast);
}

.tag:hover { color: var(--color-accent); }

.tag-more { cursor: default; }
.tag-more:hover { color: var(--color-text-muted); }

.play-btn {
  flex-shrink: 0;
  background: var(--color-accent);
  color: var(--color-text-primary);
  border: none;
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  transition: background var(--transition-fast);
  margin-left: var(--spacing-sm);
}

.play-btn:hover { background: var(--color-accent-hover); }

@media (max-width: 639px) {
  .card-top { flex-direction: column; }
  .card-cover { width: 100%; }
  .card-info { display: none; }
  .card-bottom { padding-top: var(--spacing-md); }
}
</style>
