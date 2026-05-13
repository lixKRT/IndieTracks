<!-- 专辑组件 -->
<template>
  <div class="album-card">
    <div class="album-cover-container">
      <img
        :src="album.cover"
        :alt="album.title"
        class="album-cover"
        @click="$emit('album-click', album)"
      >
    </div>

    <div class="album-info">
      <!-- 标题和艺术家 + 收藏星星 -->
      <div class="album-info-header">
        <div class="album-info-text">
          <h3 class="album-title" @click="$emit('album-click', album)">
            {{ album.title }}
          </h3>
          <div class="artist-name" @click="$emit('artist-click', album.artist)">
            @{{ album.artist }}
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
        >{{ tag }}</span>
      </div>

      <div v-if="!album.free" class="album-price">¥ {{ album.price }}</div>
      <div v-else class="album-price free">免费</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AlbumCard',
  props: {
    album: {
      type: Object,
      required: true
    }
  },
  emits: ['album-click', 'artist-click', 'tag-click', 'preview', 'favorite'],
  data() {
    return {
      favorited: false
    };
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
  background: #1a1a1a;
  border-radius: 0;
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
  border: 1px solid #222;
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

.album-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  cursor: pointer;
}

.album-info {
  padding: 0.5rem 0.8rem;
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
  padding: 0 0 0 0.5rem;
  transition: transform 0.2s;
  line-height: 1;
}
.favorite-btn .fa-star {
  color: #666;
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
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.album-title:hover {
  color: #ff6b6b;
}

.artist-name {
  display: block;
  width: fit-content;
  font-size: 0.75rem;
  color: #aaa;
  margin-bottom: 0.3rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.artist-name:hover {
  color: #ff6b6b;
}

.play-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.mini-play-btn {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  background: #ff6b6b;
  border: none;
  color: white;
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 0.7rem;
}

.mini-play-btn:hover {
  background: #ff8787;
}

.progress-bar {
  flex: 1;
  height: 3px;
  background: #333;
}

.progress-fill {
  height: 100%;
  background: #ff6b6b;
  transition: width 0.3s;
}

.album-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.2rem;
  width: fit-content;
  margin-bottom: 0.4rem;
  max-height: 36px;
  overflow: hidden;
}

.tag {
  background: #2a2a2a;
  color: #bbb;
  padding: 0.12rem 0.35rem;
  border-radius: 0;
  font-size: 0.6rem;
  cursor: pointer;
}

.tag:hover {
  background: #3a3a3a;
}

.album-price {
  font-size: 0.95rem;
  font-weight: bold;
  color: #ff6b6b;
  margin-top: 0.4rem;
}

.album-price.free {
  color: #4caf50;
}
</style>
