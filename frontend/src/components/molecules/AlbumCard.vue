<!-- 专辑卡片（分子） -->
<template>
  <div class="album-card">
    <div class="album-cover-container">
      <img
        :src="album.cover_url"
        :alt="album.title"
        class="album-cover"
        @click="$emit('album-click', album)"
      >
      <span v-if="album.price === 0" class="free-badge">免费</span>
    </div>

    <div class="album-info">
      <div class="album-info-header">
        <div class="album-info-text">
          <h3 class="album-title" @click="$emit('album-click', album)">
            {{ album.title }}
          </h3>
          <div class="circle-name" @click="$emit('circle-click', album.circle_name)">
            @{{ album.circle_name }}
          </div>
        </div>
        <div class="favorite-btn" @click.stop="toggleFavorite">
          <i class="fa-star" :class="favorited ? 'fas' : 'far'"></i>
        </div>
      </div>

      <div class="play-controls">
        <button class="mini-play-btn" @click="$emit('preview', album)">
          <i class="fas fa-play"></i>
        </button>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: (album.progress || 0) + '%' }"></div>
        </div>
      </div>

      <div class="album-tags">
        <span
          v-for="tag in album.tags.slice(0, 3)"
          :key="tag"
          class="tag"
          @click.stop="$emit('tag-click', tag)"
        >#{{ tag }}</span>
      </div>

      <div v-if="album.price > 0" class="album-price">&yen; {{ album.price }}</div>
      <div v-else class="album-price free">免费</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AlbumCard',
  props: {
    album: { type: Object, required: true }
  },
  emits: ['album-click', 'circle-click', 'tag-click', 'preview', 'favorite'],
  data() {
    return { favorited: false };
  },
  methods: {
    toggleFavorite() {
      this.favorited = !this.favorited;
      this.$emit('favorite', { album: this.album, favorited: this.favorited });
    }
  }
};
</script>

<style scoped>
.album-card {
  background: var(--color-bg-secondary);
  overflow: hidden;
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
  border: 1px solid var(--color-border);
  position: relative;
}

.album-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

.album-cover-container {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
}

.free-badge {
  position: absolute;
  top: var(--spacing-sm);
  left: var(--spacing-sm);
  background: var(--color-accent);
  color: var(--color-text-primary);
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: 600;
}

.album-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  cursor: pointer;
}

.album-info {
  padding: var(--spacing-sm) 0.8rem;
}

.album-info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.4rem;
}

.album-info-text {
  flex: 1;
  min-width: 0;
}

.favorite-btn {
  flex-shrink: 0;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 0 0 0 var(--spacing-sm);
  line-height: 1;
}

.favorite-btn .fa-star {
  color: var(--color-text-dim);
}

.favorite-btn .fa-star.fas {
  color: #f5c518;
}

.favorite-btn:hover {
  transform: scale(1.25);
}

.album-title {
  display: block;
  width: fit-content;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.album-title:hover {
  color: var(--color-accent);
}

.circle-name {
  display: block;
  width: fit-content;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-bottom: 0.3rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.circle-name:hover {
  color: var(--color-accent);
}

.play-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: 0.4rem;
}

.mini-play-btn {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  background: var(--color-accent);
  border: none;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background var(--transition-fast);
  font-size: 0.7rem;
}

.mini-play-btn:hover {
  background: var(--color-accent-hover);
}

.progress-bar {
  flex: 1;
  height: 3px;
  background: var(--color-border);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-accent);
  transition: width 0.3s;
}

.album-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-bottom: 0.3rem;
}

.tag {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 1px 6px;
  cursor: pointer;
  transition: color var(--transition-fast);
}

.tag:hover {
  color: var(--color-accent);
}

.album-price {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-accent);
}

.album-price.free {
  color: #4CAF50;
}
</style>
