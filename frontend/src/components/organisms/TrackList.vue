<!-- 曲目列表（有机体） -->
<template>
  <div class="tracklist">
    <h3 class="tracklist-title">曲目列表 ({{ tracks.length }})</h3>
    <TrackRow
      v-for="(track, index) in tracks"
      :key="track.file_id"
      :track="track"
      :index="index"
      :is_current="currentTrackId === track.file_id"
      :playing="isPlaying && currentTrackId === track.file_id"
      @preview="(track, idx) => $emit('preview', tracks, idx)"
    />
  </div>
</template>

<script>
import TrackRow from '../molecules/TrackRow.vue';
import { usePlayerStore } from '../../stores/player.js';
import { computed } from 'vue';

export default {
  name: 'TrackList',
  components: { TrackRow },
  props: { tracks: { type: Array, required: true } },
  emits: ['preview'],
  setup() {
    const player = usePlayerStore();
    return {
      currentTrackId: computed(() => player.current_track?.file_id ?? null),
      isPlaying: computed(() => player.is_playing)
    };
  }
};
</script>

<style scoped>
.tracklist { margin-top: var(--spacing-xl); }
.tracklist-title { font-size: 1.1rem; color: var(--color-text-primary); margin-bottom: var(--spacing-md); border-bottom: 1px solid var(--color-border); padding-bottom: var(--spacing-sm); }
</style>
