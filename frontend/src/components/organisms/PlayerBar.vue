<!-- 底部播放条（有机体） -->
<template>
  <aside v-if="store.playlist_length > 0" class="player-bar" :class="{ expanded: store.is_expanded }">
    <!-- 收起态 -->
    <div class="player-bar-collapsed">
      <div class="player-now-playing" @click="store.toggleExpand()">
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

    <!-- 进度条（收起态 + 展开态都显示） -->
    <div class="player-progress" @click="seekProgress">
      <div class="player-progress-track">
        <div class="player-progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
      <span class="player-progress-time">{{ formatTime(currentTime) }} / {{ store.current_track?.duration || '0:00' }}</span>
    </div>

    <!-- 展开态 -->
    <div v-if="store.is_expanded" class="player-bar-expanded">
      <div class="player-actions">
        <span class="player-count">共 {{ store.playlist_length }} 首</span>
        <button class="player-clear-btn" @click="store.clearPlaylist()">清空列表</button>
      </div>
      <div class="player-playlist">
        <div
          v-for="(track, index) in store.playlist"
          :key="'pl-' + index"
          class="playlist-row"
          :class="{ active: index === store.current_index }"
          :draggable="true"
          @dragstart="onDragStart(index, $event)"
          @dragover.prevent
          @drop="onDrop(index)"
        >
          <span class="playlist-drag-handle">⠿</span>
          <span class="playlist-index">{{ index + 1 }}</span>
          <span class="playlist-name" @click="store.setCurrentIndex(index)">{{ track.file_name }}</span>
          <span class="playlist-duration">{{ track.duration }}</span>
          <button class="playlist-remove" @click.stop="store.removeTrack(index)" title="移除">&times;</button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script>
import { usePlayerStore } from '../../stores/player.js';

export default {
  name: 'PlayerBar',
  data() {
    return {
      currentTime: 0,
      progressTimer: null,
      dragFrom: -1
    };
  },
  setup() {
    const store = usePlayerStore();
    return { store };
  },
  computed: {
    progressPercent() {
      const dur = this.parseSeconds(this.store.current_track?.duration);
      if (!dur) return 0;
      return Math.min(100, (this.currentTime / dur) * 100);
    }
  },
  watch: {
    'store.current_index'() { this.resetProgress(); },
    'store.is_playing'(val) {
      if (val) this.startProgress(); else this.stopProgress();
    }
  },
  mounted() {
    if (this.store.is_playing) this.startProgress();
  },
  beforeUnmount() {
    this.stopProgress();
  },
  methods: {
    startProgress() {
      this.stopProgress();
      this.progressTimer = setInterval(() => {
        const dur = this.parseSeconds(this.store.current_track?.duration);
        if (dur && this.currentTime >= dur) {
          this.store.next();
        } else {
          this.currentTime += 0.25;
        }
      }, 250);
    },
    stopProgress() {
      if (this.progressTimer) { clearInterval(this.progressTimer); this.progressTimer = null; }
    },
    resetProgress() {
      this.currentTime = 0;
      if (this.store.is_playing) this.startProgress();
    },
    seekProgress(e) {
      const rect = e.currentTarget.querySelector('.player-progress-track');
      if (!rect) return;
      const x = e.clientX - rect.getBoundingClientRect().left;
      const pct = x / rect.offsetWidth;
      const dur = this.parseSeconds(this.store.current_track?.duration);
      if (dur) this.currentTime = Math.round(pct * dur);
    },
    parseSeconds(dur) {
      if (!dur) return 0;
      const parts = dur.split(':').map(Number);
      if (parts.length === 2) return parts[0] * 60 + parts[1];
      return 0;
    },
    formatTime(sec) {
      const m = Math.floor(sec / 60);
      const s = Math.floor(sec % 60);
      return m + ':' + String(s).padStart(2, '0');
    },
    onDragStart(index, e) {
      this.dragFrom = index;
      e.dataTransfer.effectAllowed = 'move';
    },
    onDrop(to) {
      if (this.dragFrom >= 0 && this.dragFrom !== to) {
        this.store.reorder(this.dragFrom, to);
      }
      this.dragFrom = -1;
    }
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

/* ---- 收起态 ---- */
.player-bar-collapsed {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-lg);
  height: 56px;
}

.player-now-playing {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
  cursor: pointer;
}

.player-track-name {
  font-size: 0.85rem;
  color: var(--color-text-primary);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.player-track-artist { font-size: 0.75rem; color: var(--color-text-muted); }

.player-controls-mini {
  display: flex; align-items: center; gap: var(--spacing-sm); flex-shrink: 0;
}

.player-btn {
  background: none; border: none; color: var(--color-text-secondary);
  font-size: 1rem; padding: var(--spacing-xs); cursor: pointer;
  transition: color var(--transition-fast);
}
.player-btn:hover { color: var(--color-accent); }

.player-btn-play {
  width: 36px; height: 36px;
  background: var(--color-accent); color: var(--color-text-primary);
  display: flex; align-items: center; justify-content: center; font-size: 0.9rem;
}
.player-btn-play:hover { background: var(--color-accent-hover); color: var(--color-text-primary); }

/* ---- 进度条 ---- */
.player-progress {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: 0 var(--spacing-lg) 2px;
  cursor: pointer;
}
.player-progress-track {
  flex: 1; height: 3px; background: var(--color-border); overflow: hidden;
}
.player-progress-fill {
  height: 100%; background: var(--color-accent); transition: width 0.25s linear;
}
.player-progress-time {
  font-size: 0.65rem; color: var(--color-text-dim); flex-shrink: 0; min-width: 60px; text-align: right;
}

/* ---- 展开态 ---- */
.player-bar-expanded {
  max-height: 320px; overflow-y: auto; border-top: 1px solid var(--color-border);
  scrollbar-width: thin;
  scrollbar-color: var(--color-border) transparent;
}
.player-bar-expanded::-webkit-scrollbar { width: 4px; }
.player-bar-expanded::-webkit-scrollbar-track { background: transparent; }
.player-bar-expanded::-webkit-scrollbar-thumb { background: var(--color-border); }
.player-bar-expanded::-webkit-scrollbar-thumb:hover { background: var(--color-border-light); }
.player-playlist { padding: var(--spacing-sm); }

.playlist-row {
  display: flex; align-items: center; gap: var(--spacing-sm);
  padding: 0.5rem var(--spacing-sm); cursor: grab;
  transition: background var(--transition-fast);
}
.playlist-row:hover { background: rgba(255, 255, 255, 0.03); }
.playlist-row.active { background: rgba(255, 107, 107, 0.1); border-left: 3px solid var(--color-accent); }

.playlist-drag-handle {
  font-size: 0.7rem; color: var(--color-text-dim); cursor: grab; flex-shrink: 0;
  user-select: none;
}

.playlist-index {
  font-size: 0.75rem; color: var(--color-text-dim); width: 24px; text-align: center; flex-shrink: 0;
}
.playlist-name {
  flex: 1; font-size: 0.8rem; color: var(--color-text-primary);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer;
}
.playlist-duration { font-size: 0.75rem; color: var(--color-text-dim); flex-shrink: 0; }

.playlist-remove {
  background: none; border: none; color: var(--color-text-dim);
  font-size: 1.1rem; cursor: pointer; padding: 0 4px; transition: color var(--transition-fast);
}
.playlist-remove:hover { color: var(--color-accent); }

/* ---- 操作栏 ---- */
.player-actions {
  display: flex; justify-content: space-between; align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
}
.player-count { font-size: 0.75rem; color: var(--color-text-dim); }
.player-clear-btn {
  background: none; border: 1px solid var(--color-border);
  color: var(--color-text-muted); padding: 0.2rem 0.8rem; font-size: 0.75rem;
  cursor: pointer; transition: all var(--transition-fast);
}
.player-clear-btn:hover { border-color: var(--color-accent); color: var(--color-accent); }
</style>
