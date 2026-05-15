import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';

const STORAGE_KEY = 'indietracks_player';

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function saveState(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // localStorage 满或不可用，静默失败
  }
}

export const usePlayerStore = defineStore('player', () => {
  const saved = loadState();

  const playlist = ref(saved?.playlist ?? []);
  const current_index = ref(saved?.current_index ?? -1);
  const is_playing = ref(false);
  const is_expanded = ref(false);

  const current_track = computed(() => {
    if (current_index.value < 0 || current_index.value >= playlist.value.length) {
      return null;
    }
    return playlist.value[current_index.value];
  });

  const playlist_length = computed(() => playlist.value.length);

  // 添加整张专辑的 preview 曲目到播放列表末尾
  function addAlbumTracks(tracks, start_index) {
    const preview_tracks = tracks.filter(t => t.file_type === 'preview');
    if (preview_tracks.length === 0) return;

    const insert_pos = playlist.value.length;
    playlist.value.push(...preview_tracks);
    setCurrentIndex(insert_pos + (start_index ?? 0));
  }

  // 替换播放列表为整张专辑曲目，从指定曲目开始播放
  function playAlbumTracks(tracks, start_index) {
    const preview_tracks = tracks.filter(t => t.file_type === 'preview');
    if (preview_tracks.length === 0) return;

    playlist.value = [...preview_tracks];
    setCurrentIndex(start_index ?? 0);
  }

  // 在播放列表中查找曲目并跳转
  function jumpToTrack(file_id) {
    const idx = playlist.value.findIndex(t => t.file_id === file_id);
    if (idx >= 0) setCurrentIndex(idx);
  }

  function setCurrentIndex(index) {
    if (index >= 0 && index < playlist.value.length) {
      current_index.value = index;
      is_playing.value = true;
      is_expanded.value = true;
    }
  }

  function togglePlay() {
    if (current_track.value) {
      is_playing.value = !is_playing.value;
    }
  }

  function prev() {
    if (playlist.value.length === 0) return;
    const idx = current_index.value <= 0
      ? playlist.value.length - 1
      : current_index.value - 1;
    setCurrentIndex(idx);
  }

  function next() {
    if (playlist.value.length === 0) return;
    const idx = current_index.value >= playlist.value.length - 1
      ? 0
      : current_index.value + 1;
    setCurrentIndex(idx);
  }

  function reorder(from, to) {
    const item = playlist.value.splice(from, 1)[0];
    playlist.value.splice(to, 0, item);

    if (current_index.value === from) {
      current_index.value = to;
    } else if (from < current_index.value && to >= current_index.value) {
      current_index.value--;
    } else if (from > current_index.value && to <= current_index.value) {
      current_index.value++;
    }
  }

  function removeTrack(index) {
    playlist.value.splice(index, 1);
    if (playlist.value.length === 0) {
      current_index.value = -1;
      is_playing.value = false;
    } else if (index <= current_index.value) {
      current_index.value = Math.max(0, current_index.value - 1);
    }
  }

  function clearPlaylist() {
    playlist.value = [];
    current_index.value = -1;
    is_playing.value = false;
    is_expanded.value = false;
  }

  function toggleExpand() {
    is_expanded.value = !is_expanded.value;
  }

  // localStorage 持久化
  watch(
    [playlist, current_index],
    () => {
      saveState({
        playlist: playlist.value,
        current_index: current_index.value
      });
    },
    { deep: true }
  );

  return {
    playlist,
    current_index,
    is_playing,
    is_expanded,
    current_track,
    playlist_length,
    addAlbumTracks,
    playAlbumTracks,
    jumpToTrack,
    setCurrentIndex,
    togglePlay,
    prev,
    next,
    reorder,
    removeTrack,
    clearPlaylist,
    toggleExpand
  };
});
