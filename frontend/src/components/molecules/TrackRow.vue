<!-- 曲目行（分子） -->
<template>
  <div class="track-row" :class="{ active: is_current }" @click="$emit('preview', track, index)">
    <span class="track-index">{{ pad(index + 1) }}</span>
    <span class="track-name">{{ track.file_name }}</span>
    <span class="track-duration">{{ track.duration }}</span>
    <button class="track-preview-btn" @click="$emit('preview', track, index)">
      <i :class="is_current && playing ? 'fas fa-volume-up' : 'fas fa-play'"></i>
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
    pad(n) { return String(n).padStart(2, '0'); }
  }
};
</script>

<style scoped>
.track-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 0.6rem var(--spacing-md);
  transition: background var(--transition-fast);
  cursor: pointer;
}

.track-row:hover { background: rgba(255, 255, 255, 0.02); }
.track-row.active { background: rgba(255, 107, 107, 0.08); border-left: 3px solid var(--color-accent); }

.track-index { font-size: 0.8rem; color: var(--color-text-dim); width: 28px; flex-shrink: 0; text-align: center; }
.track-name { flex: 1; font-size: 0.85rem; color: var(--color-text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.track-duration { font-size: 0.8rem; color: var(--color-text-dim); flex-shrink: 0; }

.track-preview-btn {
  flex-shrink: 0;
  background: none;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  opacity: 0;
}

.track-row:hover .track-preview-btn { opacity: 1; }
.track-preview-btn:hover { border-color: var(--color-accent); color: var(--color-accent); opacity: 1; }
.active .track-preview-btn { border-color: var(--color-accent); color: var(--color-accent); opacity: 1; }
</style>
