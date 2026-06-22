<template>
  <div class="album-list-page">
    <div class="page-header">
      <h1 class="page-title">专辑管理</h1>
      <router-link to="/admin/albums/create" class="btn-create">
        <i class="fas fa-plus"></i> 新增专辑
      </router-link>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="搜索专辑名称..."
        class="search-input"
        @keyup.enter="loadAlbums"
      />
      <button class="btn-search" @click="loadAlbums">
        <i class="fas fa-search"></i>
      </button>
    </div>

    <!-- 专辑列表 -->
    <LoadingSpinner v-if="loading" />

    <template v-else>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>封面</th>
              <th>标题</th>
              <th>社团</th>
              <th>价格</th>
              <th>发布时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="album in albums" :key="album.album_id">
              <td>
                <img :src="album.cover_url" :alt="album.title" class="album-cover" />
              </td>
              <td>
                <span class="album-title">{{ album.title }}</span>
              </td>
              <td>
                <span class="album-circle">{{ album.circle_name || '-' }}</span>
              </td>
              <td>
                <span v-if="album.price > 0" class="price-paid">¥{{ album.price }}</span>
                <span v-else class="price-free">免费</span>
              </td>
              <td>
                <span class="album-date">{{ formatDate(album.publish_date) }}</span>
              </td>
              <td>
                <div class="action-buttons">
                  <router-link :to="`/admin/albums/${album.album_id}/edit`" class="btn-action btn-edit">
                    <i class="fas fa-edit"></i>
                  </router-link>
                  <button class="btn-action btn-delete" @click="handleDelete(album)">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="pagination" v-if="totalPages > 1">
        <button
          class="page-btn"
          :disabled="currentPage <= 1"
          @click="currentPage--; loadAlbums()"
        >上一页</button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button
          class="page-btn"
          :disabled="currentPage >= totalPages"
          @click="currentPage++; loadAlbums()"
        >下一页</button>
      </div>
    </template>
  </div>
</template>

<script>
import { getAdminAlbums, deleteAlbum } from '../../api/admin.js';
import LoadingSpinner from '../../components/atoms/LoadingSpinner.vue';

export default {
  name: 'AdminAlbumList',
  components: { LoadingSpinner },
  data() {
    return {
      albums: [],
      loading: true,
      searchQuery: '',
      currentPage: 1,
      pageSize: 20,
      totalAlbums: 0
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalAlbums / this.pageSize);
    }
  },
  async mounted() {
    await this.loadAlbums();
  },
  methods: {
    async loadAlbums() {
      this.loading = true;
      try {
        const result = await getAdminAlbums({
          page: this.currentPage,
          page_size: this.pageSize,
          search: this.searchQuery || undefined
        });
        this.albums = result.data || [];
        this.totalAlbums = result.total || 0;
      } catch (e) {
        console.error('加载专辑失败:', e);
      } finally {
        this.loading = false;
      }
    },
    async handleDelete(album) {
      if (!confirm(`确定删除专辑「${album.title}」？`)) return;
      try {
        await deleteAlbum(album.album_id);
        await this.loadAlbums();
      } catch (e) {
        console.error('删除失败:', e);
        alert('删除失败');
      }
    },
    formatDate(date) {
      if (!date) return '-';
      return new Date(date).toLocaleDateString('zh-CN');
    }
  }
};
</script>

<style scoped>
.album-list-page {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.btn-create {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-accent);
  color: var(--color-text-primary);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background var(--transition-fast);
}

.btn-create:hover {
  background: var(--color-accent-hover);
}

/* 搜索栏 */
.search-bar {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
}

.search-input {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  font-size: 0.9rem;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.btn-search {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-search:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

/* 表格 */
.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: var(--spacing-md);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.data-table th {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
}

.data-table tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.album-cover {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border: 1px solid var(--color-border);
}

.album-title {
  font-size: 0.9rem;
  color: var(--color-text-primary);
}

.album-circle {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.price-paid {
  font-weight: 600;
  color: var(--color-accent);
}

.price-free {
  color: #4caf50;
}

.album-date {
  font-size: 0.85rem;
  color: var(--color-text-dim);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-action {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
  font-size: 0.85rem;
}

.btn-action:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.btn-delete:hover {
  border-color: #e53935;
  color: #e53935;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
}

.page-btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.page-btn:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.9rem;
  color: var(--color-text-muted);
}
</style>
