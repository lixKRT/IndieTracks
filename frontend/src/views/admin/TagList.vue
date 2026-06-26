<!-- AdminTagList — 管理后台标签列表，支持搜索、新增弹窗与删除 -->
<template>
  <div class="tag-list-page">
    <div class="page-header">
      <h1 class="page-title">标签管理</h1>
      <button class="btn-create" @click="showCreate = true">
        <i class="fas fa-plus"></i> 新增标签
      </button>
    </div>

    <div class="search-bar">
      <input type="text" v-model="searchQuery" placeholder="搜索标签名..." class="search-input" @keyup.enter="loadTags" />
      <button class="btn-search" @click="loadTags"><i class="fas fa-search"></i></button>
    </div>

    <LoadingSpinner v-if="loading" />

    <template v-else>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>标签名</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tag in tags" :key="tag.tag_id">
              <td>{{ tag.tag_id }}</td>
              <td>
                <span class="tag-name">#{{ tag.name }}</span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn-action btn-delete" @click="handleDelete(tag)">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- 新增弹窗 -->
    <Teleport to="body">
      <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>新增标签</h3>
            <button class="modal-close" @click="showCreate = false">&times;</button>
          </div>
          <form @submit.prevent="handleCreate" class="modal-body">
            <div class="form-group">
              <label>标签名</label>
              <input type="text" v-model="newTagName" required placeholder="输入标签名" />
            </div>
            <div class="form-actions">
              <button type="button" class="btn-cancel" @click="showCreate = false">取消</button>
              <button type="submit" class="btn-submit">创建</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { getAdminTags, createTag, deleteTag } from '../../api/admin.js';
import LoadingSpinner from '../../components/atoms/LoadingSpinner.vue';

export default {
  name: 'AdminTagList',
  components: { LoadingSpinner },
  data() {
    return {
      tags: [],
      loading: true,
      showCreate: false,
      newTagName: '',
      searchQuery: ''
    };
  },
  async mounted() {
    await this.loadTags();
  },
  methods: {
    // 标签无分页，一次加载全部
    async loadTags() {
      this.loading = true;
      try {
        const result = await getAdminTags({ search: this.searchQuery || undefined });
        // 兼容 { data } 和直接数组两种响应格式
        this.tags = result.data || result || [];
      } catch (e) {
        console.error('加载标签失败:', e);
      } finally {
        this.loading = false;
      }
    },
    async handleCreate() {
      try {
        await createTag({ name: this.newTagName });
        this.newTagName = '';
        this.showCreate = false;
        await this.loadTags();
      } catch (e) {
        console.error('创建失败:', e);
        alert('创建失败');
      }
    },
    async handleDelete(tag) {
      if (!confirm(`确定删除标签「#${tag.name}」？`)) return;
      try {
        await deleteTag(tag.tag_id);
        await this.loadTags();
      } catch (e) {
        console.error('删除失败:', e);
        alert('删除失败');
      }
    }
  }
};
</script>

<style scoped>
.tag-list-page {
  max-width: 800px;
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
  border: none;
  color: var(--color-text-primary);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.btn-create:hover {
  background: var(--color-accent-hover);
}

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
}

.tag-name {
  font-size: 0.9rem;
  color: var(--color-accent);
}

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
}

.btn-delete:hover {
  border-color: #e53935;
  color: #e53935;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  width: 400px;
  max-width: 90vw;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  font-size: 1rem;
  color: var(--color-text-primary);
}

.modal-close {
  background: none;
  border: none;
  color: var(--color-text-dim);
  font-size: 1.2rem;
  cursor: pointer;
}

.modal-body {
  padding: var(--spacing-lg);
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-xs);
}

.form-group input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.form-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
}

.btn-cancel {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  cursor: pointer;
}

.btn-submit {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-accent);
  border: none;
  color: var(--color-text-primary);
  font-weight: 600;
  cursor: pointer;
}
</style>
