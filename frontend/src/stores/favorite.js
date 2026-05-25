import { defineStore } from 'pinia';

export const useFavoriteStore = defineStore('favorite', {
  state: () => ({
    // 使用 Set 存储已收藏的专辑 ID，便于快速查找
    favoriteAlbumIds: new Set()
  }),
  
  getters: {
    // 检查专辑是否已收藏
    isFavorite: (state) => (albumId) => {
      return state.favoriteAlbumIds.has(albumId);
    },
    
    // 获取所有收藏的专辑 ID 数组
    favoriteIdsArray: (state) => {
      return Array.from(state.favoriteAlbumIds);
    }
  },
  
  actions: {
    // 初始化时从 localStorage 加载
    initFromStorage() {
      try {
        const stored = localStorage.getItem('indie-tracks-favorites');
        if (stored) {
          const ids = JSON.parse(stored);
          this.favoriteAlbumIds = new Set(ids);
        }
      } catch (e) {
        console.error('加载收藏数据失败:', e);
      }
    },
    
    // 切换收藏状态
    toggleFavorite(albumId) {
      if (this.favoriteAlbumIds.has(albumId)) {
        this.favoriteAlbumIds.delete(albumId);
      } else {
        this.favoriteAlbumIds.add(albumId);
      }
      // 保存到 localStorage
      this.saveToStorage();
      console.log(`专辑 ${albumId} 收藏状态已更新`);
    },
    
    // 添加收藏
    addFavorite(albumId) {
      this.favoriteAlbumIds.add(albumId);
      this.saveToStorage();
    },
    
    // 取消收藏
    removeFavorite(albumId) {
      this.favoriteAlbumIds.delete(albumId);
      this.saveToStorage();
    },
    
    // 批量设置收藏状态（用于从后端加载数据时）
    setFavorites(albumIds) {
      this.favoriteAlbumIds = new Set(albumIds);
      this.saveToStorage();
    },
    
    // 保存到 localStorage
    saveToStorage() {
      try {
        localStorage.setItem('indie-tracks-favorites', JSON.stringify(Array.from(this.favoriteAlbumIds)));
      } catch (e) {
        console.error('保存收藏数据失败:', e);
      }
    }
  }
});
