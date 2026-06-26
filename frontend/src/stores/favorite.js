// 收藏 Store — 管理用户收藏的专辑 ID 列表（Options API 风格）
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
    // 乐观更新：先修改本地状态，再同步后端
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

    // 单个专辑收藏状态检查，同步本地缓存
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

    // 加载全部收藏列表，后端返回 snake_case 字段
    async loadAll() {
      try {
        const data = await getFavorites();
        this.favoriteAlbumIds = data.map(a => a.album_id);
      } catch { this.favoriteAlbumIds = []; }
    }
  }
});
