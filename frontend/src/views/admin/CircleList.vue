<!-- AdminCircleList — 管理后台社团列表，支持搜索与分页 -->
<template>
  <div class="circle-list-page">
    <h1 class="page-title">社团管理</h1>

    <div class="search-bar">
      <input type="text" v-model="searchQuery" placeholder="搜索社团名称..." class="search-input" @keyup.enter="loadCircles" />
      <button class="btn-search" @click="loadCircles"><i class="fas fa-search"></i></button>
    </div>

    <LoadingSpinner v-if="loading" />

    <template v-else>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Logo</th>
              <th>名称</th>
              <th>成员数</th>
              <th>专辑数</th>
              <th>描述</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="circle in circles" :key="circle.circle_id">
              <td><img :src="circle.logo_url" :alt="circle.name" class="circle-logo" /></td>
              <td><span class="circle-name">{{ circle.name }}</span></td>
              <td>{{ circle.member_count || 0 }}</td>
              <td>{{ circle.album_count || 0 }}</td>
              <td><span class="circle-desc">{{ truncate(circle.description, 30) }}</span></td>
              <td>
                <div class="action-buttons">
                  <router-link :to="`/admin/circles/${circle.circle_id}`" class="btn-action btn-edit"><i class="fas fa-eye"></i></router-link>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination" v-if="totalPages > 1">
        <button class="page-btn" :disabled="currentPage <= 1" @click="currentPage--; loadCircles()">上一页</button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="currentPage++; loadCircles()">下一页</button>
      </div>
    </template>
  </div>
</template>

<script>
import { getAdminCircles } from '../../api/admin.js';
import LoadingSpinner from '../../components/atoms/LoadingSpinner.vue';

export default {
  name: 'AdminCircleList',
  components: { LoadingSpinner },
  data() {
    return { circles: [], loading: true, searchQuery: '', currentPage: 1, pageSize: 20, totalCircles: 0 };
  },
  computed: {
    totalPages() { return Math.ceil(this.totalCircles / this.pageSize); }
  },
  async mounted() { await this.loadCircles(); },
  methods: {
    async loadCircles() {
      this.loading = true;
      try {
        // 空搜索时传 undefined，避免向后端发送空字符串参数
        const result = await getAdminCircles({ page: this.currentPage, page_size: this.pageSize, search: this.searchQuery || undefined });
        this.circles = result.data || [];
        this.totalCircles = result.total || 0;
      } catch (e) { console.error('加载社团失败:', e); }
      finally { this.loading = false; }
    },
    // JS 截断用于表格单元格内文本，比 CSS text-overflow 更可控
    truncate(text, len) { if (!text) return '-'; return text.length > len ? text.slice(0, len) + '...' : text; }
  }
};
</script>

<style scoped>
.circle-list-page { max-width: 1200px; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text-primary); margin-bottom: var(--spacing-xl); }
.search-bar { display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-lg); }
.search-input { flex: 1; padding: var(--spacing-sm) var(--spacing-md); background: var(--color-bg-secondary); border: 1px solid var(--color-border); color: var(--color-text-primary); font-size: 0.9rem; }
.search-input:focus { outline: none; border-color: var(--color-accent); }
.btn-search { padding: var(--spacing-sm) var(--spacing-md); background: var(--color-bg-secondary); border: 1px solid var(--color-border); color: var(--color-text-muted); cursor: pointer; }
.btn-search:hover { border-color: var(--color-accent); color: var(--color-accent); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: var(--spacing-md); text-align: left; border-bottom: 1px solid var(--color-border); }
.data-table th { font-size: 0.8rem; font-weight: 600; color: var(--color-text-muted); }
.data-table tr:hover { background: rgba(255,255,255,0.02); }
.circle-logo { width: 40px; height: 40px; object-fit: cover; border: 1px solid var(--color-border); }
.circle-name { font-size: 0.9rem; color: var(--color-text-primary); }
.circle-desc { font-size: 0.8rem; color: var(--color-text-muted); }
.action-buttons { display: flex; gap: var(--spacing-sm); }
.btn-action { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: transparent; border: 1px solid var(--color-border); color: var(--color-text-muted); text-decoration: none; cursor: pointer; }
.btn-action:hover { border-color: var(--color-accent); color: var(--color-accent); }
.pagination { display: flex; justify-content: center; align-items: center; gap: var(--spacing-md); margin-top: var(--spacing-xl); }
.page-btn { padding: var(--spacing-sm) var(--spacing-lg); background: var(--color-bg-secondary); border: 1px solid var(--color-border); color: var(--color-text-muted); cursor: pointer; }
.page-btn:hover:not(:disabled) { border-color: var(--color-accent); color: var(--color-accent); }
.page-btn:disabled { opacity: 0.5; }
.page-info { font-size: 0.9rem; color: var(--color-text-muted); }
</style>
