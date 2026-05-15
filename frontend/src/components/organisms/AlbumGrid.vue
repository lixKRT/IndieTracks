<!-- 专辑网格（有机体） -->
<template>
  <div class="album-grid-container container">
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="albums.length === 0" class="empty-state">
      <p>暂无专辑</p>
    </div>

    <div v-else class="album-grid">
      <AlbumCard
        v-for="album in visibleAlbums"
        :key="album.album_id"
        :album="album"
        @album-click="album => $emit('album-click', album)"
        @circle-click="name => $emit('circle-click', name)"
        @tag-click="tag => $emit('tag-click', tag)"
        @preview="album => $emit('preview', album)"
      />
    </div>

    <div v-if="!showAll && albums.length > maxVisible" class="view-all-container">
      <button class="btn-view-all" @click="$emit('view-all')">展开全部</button>
    </div>
  </div>
</template>

<script>
import AlbumCard from '../../components/molecules/AlbumCard.vue';

export default {
  name: 'AlbumGrid',
  components: { AlbumCard },
  props: {
    albums: { type: Array, default: () => [] },
    loading: { type: Boolean, default: true },
    showAll: { type: Boolean, default: false },
    maxVisible: { type: Number, default: 6 }
  },
  emits: ['album-click', 'circle-click', 'tag-click', 'preview', 'view-all'],
  computed: {
    visibleAlbums() {
      return this.showAll ? this.albums : this.albums.slice(0, this.maxVisible);
    }
  }
};
</script>

<style scoped>
.album-grid-container {
  padding-top: var(--spacing-xl);
}

.album-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
}

@media (min-width: 640px) {
  .album-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1024px) {
  .album-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.view-all-container {
  display: flex;
  justify-content: center;
  margin: var(--spacing-lg) 0 var(--spacing-2xl);
}

.btn-view-all {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  padding: 0.8rem 9rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-normal);
}

.btn-view-all:hover {
  background: var(--color-bg-secondary);
}
</style>
