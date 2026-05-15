<!-- 底部播放条（有机体）— 占位 -->
<template>
  <aside v-if="store.playlist_length > 0" class="player-bar" :class="{ expanded: store.is_expanded }">
    <div class="player-bar-collapsed" @click="store.toggleExpand()">
      <div class="player-now-playing">
        <span class="player-track-name">{{ store.current_track?.file_name || '未选择曲目' }}</span>
        <span class="player-track-artist">{{ store.current_track?.artist || '' }}</span>
      </div>
      <div class="player-controls-mini">
        <button class="player-btn" @click.stop="store.prev()"><i class="fas fa-step-backward"></i></button>
        <button class="player-btn player-btn-play" @click.stop="store.togglePlay()">
          <i :class="store.is_playing ? 'fas fa-pause' : 'fas fa-play'"></i>
        </button>
        <button class="player-btn" @click.stop="store.next()"><i class="fas fa-step-forward"></i></button>
      </div>
    </div>

    <div v-if="store.is_expanded" class="player-bar-expanded">
      <div class="player-playlist">
        <div
          v-for="(track, index) in store.playlist"
          :key="index"
          class="playlist-row"
          :class="{ active: index === store.current_index }"
          @click="store.setCurrentIndex(index)"
        >
          <span class="playlist-index">{{ index + 1 }}</span>
          <span class="playlist-name">{{ track.file_name }}</span>
          <span class="playlist-duration">{{ track.duration }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script>
import { usePlayerStore } from '../../stores/player.js';

export default {
  name: 'PlayerBar',
  setup() {
    const store = usePlayerStore();
    return { store };
  }
};
</script>

<style scoped>
.player-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
  z-index: 200;
}

.player-bar-collapsed {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-lg);
  cursor: pointer;
  height: 56px;
}

.player-bar-collapsed:hover {
  background: rgba(255, 255, 255, 0.02);
}

.player-now-playing {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.player-track-name {
  font-size: 0.85rem;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.player-track-artist {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.player-controls-mini {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

.player-btn {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: 1rem;
  padding: var(--spacing-xs);
  cursor: pointer;
  transition: color var(--transition-fast);
}

.player-btn:hover {
  color: var(--color-accent);
}

.player-btn-play {
  width: 36px;
  height: 36px;
  background: var(--color-accent);
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.player-btn-play:hover {
  background: var(--color-accent-hover);
  color: var(--color-text-primary);
}

.player-bar-expanded {
  max-height: 300px;
  overflow-y: auto;
  border-top: 1px solid var(--color-border);
}

.player-playlist {
  padding: var(--spacing-sm);
}

.playlist-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 0.5rem var(--spacing-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.playlist-row:hover {
  background: rgba(255, 255, 255, 0.03);
}

.playlist-row.active {
  background: rgba(255, 107, 107, 0.1);
  border-left: 3px solid var(--color-accent);
}

.playlist-index {
  font-size: 0.75rem;
  color: var(--color-text-dim);
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.playlist-name {
  flex: 1;
  font-size: 0.8rem;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.playlist-duration {
  font-size: 0.75rem;
  color: var(--color-text-dim);
  flex-shrink: 0;
}
</style>
