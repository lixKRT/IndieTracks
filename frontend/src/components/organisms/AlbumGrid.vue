<!-- 专辑网格（有机体） -->
<template>
  <div class="album-grid-container">
    <LoadingSpinner v-if="loading" />

    <EmptyState v-else-if="albums.length === 0" message="暂无专辑" />

    <div class="album-grid">
      <AlbumCard
        v-for="album in albums"
        :key="album.album_id"
        :album="album"
        :is-favorited="favoritedIds.includes(album.album_id)"
        @album-click="album => $emit('album-click', album)"
        @circle-click="album => $emit('circle-click', album)"
        @tag-click="tag => $emit('tag-click', tag)"
        @preview="album => $emit('preview', album)"
        @toggle-favorite="album => $emit('toggle-favorite', album)"
      />
    </div>

    <div v-if="hasMore || loadingMore" class="view-all-container">
      <button class="btn-view-all" @click="$emit('load-more')" :disabled="loadingMore">
        {{ loadingMore ? '加载中...' : '加载更多' }}
      </button>
    </div>
  </div>
</template>

<script>
import AlbumCard from '../../components/molecules/AlbumCard.vue';
import LoadingSpinner from '../../components/atoms/LoadingSpinner.vue';
import EmptyState from '../../components/atoms/EmptyState.vue';

export default {
  name: 'AlbumGrid',
  components: { AlbumCard, LoadingSpinner, EmptyState },
  props: {
    albums: { type: Array, default: () => [] },
    loading: { type: Boolean, default: true },
    loadingMore: { type: Boolean, default: false },
    hasMore: { type: Boolean, default: false },
    favoritedIds: { type: Array, default: () => [] }
  },
  emits: ['album-click', 'circle-click', 'tag-click', 'preview', 'load-more', 'toggle-favorite']
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
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .album-grid {
    grid-template-columns: repeat(2, 1fr);
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
