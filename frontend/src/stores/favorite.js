import { defineStore } from 'pinia';
import { addFavorite, removeFavorite, checkFavorite, getFavorites } from '../api';

export const useFavoriteStore = defineStore('favorite', {
  state: () => ({
    favoriteAlbumIds: []
  }),

  getters: {
    isFavorite: (state) => (albumId) => state.favoriteAlbumIds.includes(albumId)
  },

  actions: {
    async toggleFavorite(albumId) {
      const idx = this.favoriteAlbumIds.indexOf(albumId);
      if (idx >= 0) {
        await removeFavorite(albumId);
        this.favoriteAlbumIds.splice(idx, 1);
      } else {
        await addFavorite(albumId);
        this.favoriteAlbumIds.push(albumId);
      }
    },

    async check(albumId) {
      try {
        const data = await checkFavorite(albumId);
        const idx = this.favoriteAlbumIds.indexOf(albumId);
        if (data.favorited && idx < 0) {
          this.favoriteAlbumIds.push(albumId);
        } else if (!data.favorited && idx >= 0) {
          this.favoriteAlbumIds.splice(idx, 1);
        }
        return data.favorited;
      } catch { return false; }
    },

    async loadAll() {
      try {
        const data = await getFavorites();
        this.favoriteAlbumIds = data.map(a => a.album_id);
      } catch { this.favoriteAlbumIds = []; }
    }
  }
});
