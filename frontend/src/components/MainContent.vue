<template>
  <main>
    <div class="container">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else class="album-grid">
        <AlbumCard
          v-for="album in visibleAlbums"
          :key="album.id"
          :album="album"
          @album-click="album => $emit('album-click', album)"
          @artist-click="artist => $emit('artist-click', artist)"
          @tag-click="tag => $emit('tag-click', tag)"
          @preview="album => $emit('preview', album)"
        />
      </div>

      <div class="view-all-container" v-if="!showAll">
        <button class="btn-view-all" @click="$emit('view-all')">展开全部</button>
      </div>
    </div>
  </main>
</template>

<script>
import AlbumCard from './AlbumCard.vue';

export default {
  name: 'MainContent',
  components: { AlbumCard },
  props: {
    albums: { type: Array, default: () => [] },
    loading: { type: Boolean, default: true },
    showAll: { type: Boolean, default: false },
    maxVisible: { type: Number, default: 6 }
  },
  emits: ['album-click', 'artist-click', 'tag-click', 'preview', 'view-all'],
  computed: {
    visibleAlbums() {
      return this.showAll ? this.albums : this.albums.slice(0, this.maxVisible);
    }
  }
};
</script>

<style scoped>
.album-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.view-all-container {
  display: flex;
  justify-content: center;
  margin: 1.5rem 0 3rem;
}

.btn-view-all {
  background: #0a0a0a;
  color: white;
  border: 1px solid #222;
  padding: 0.8rem 9rem;
  border-radius: 0;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-view-all:hover {
  background: #1a1a1a;
}
</style>