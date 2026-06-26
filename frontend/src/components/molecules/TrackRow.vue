<!-- 曲目行（分子） -->
<template>
  <div class="track-row" :class="{ active: is_current }" @click="$emit('preview', track, index)">
    <!-- 当前播放曲目显示动画指示器，否则显示补零序号 -->
    <span class="track-index">
      <span v-if="is_current && playing" class="playing-indicator">
        <span></span><span></span><span></span>
      </span>
      <span v-else>{{ pad(index + 1) }}</span>
    </span>
    <span class="track-name" :class="{ 'is-playing': is_current && playing }">{{ track.file_name }}</span>
    <span class="track-duration">{{ track.track_length }}</span>
    <button class="track-preview-btn" @click="$emit('preview', track, index)">
      <i :class="is_current && playing ? 'fas fa-pause' : 'fas fa-play'"></i>
    </button>
  </div>
</template>

<script>
export default {
  name: 'TrackRow',
  props: {
    track: { type: Object, required: true },
    index: { type: Number, required: true },
    is_current: { type: Boolean, default: false },
    playing: { type: Boolean, default: false }
  },
  emits: ['preview'],
  methods: {
    // 序号补零：1 → "01"，10 → "10"
    pad(n) { return String(n).padStart(2, '0'); }
  }
};
</script>

<style scoped>
.track-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 0.7rem var(--spacing-md);
  transition: background var(--transition-fast);
  cursor: pointer;
  border-left: 3px solid transparent;
}

.track-row:hover { background: rgba(255, 255, 255, 0.03); }
.track-row.active { background: rgba(255, 107, 107, 0.06); border-left-color: var(--color-accent); }

.track-index {
  font-size: 0.8rem;
  color: var(--color-text-dim);
  width: 28px;
  flex-shrink: 0;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 音乐均衡器动画：3 根条交替缩放 */
.playing-indicator {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 14px;
}

.playing-indicator span {
  display: block;
  width: 3px;
  background: var(--color-accent);
  animation: playing-bar 0.8s ease-in-out infinite;
}

.playing-indicator span:nth-child(1) { height: 60%; animation-delay: 0s; }
.playing-indicator span:nth-child(2) { height: 100%; animation-delay: 0.2s; }
.playing-indicator span:nth-child(3) { height: 40%; animation-delay: 0.4s; }

@keyframes playing-bar {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.4); }
}

.track-name {
  flex: 1;
  font-size: 0.85rem;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color var(--transition-fast);
}

.track-name.is-playing { color: var(--color-accent); }

.track-duration { font-size: 0.8rem; color: var(--color-text-dim); flex-shrink: 0; }

.track-preview-btn {
  flex-shrink: 0;
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  opacity: 0; /* 默认隐藏，hover 行时显示 */
  font-size: 0.7rem;
}

.track-row:hover .track-preview-btn { opacity: 1; }
.track-preview-btn:hover { border-color: var(--color-accent); color: var(--color-accent); opacity: 1; }
.active .track-preview-btn { border-color: var(--color-accent); color: var(--color-accent); opacity: 1; }
.active .track-preview-btn:hover { background: var(--color-accent); color: var(--color-text-primary); }
</style>
