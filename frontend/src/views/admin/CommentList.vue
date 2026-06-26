<!-- AdminCommentList — 管理后台评论列表，支持分页与删除 -->
<template>
  <div class="comment-list-page">
    <h1 class="page-title">评论管理</h1>

    <LoadingSpinner v-if="loading" />

    <template v-else>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>用户</th>
              <th>专辑</th>
              <th>内容</th>
              <th>时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="comment in comments" :key="comment.comment_id">
              <td>
                <div class="user-info">
                  <img v-if="comment.avatar_url" :src="comment.avatar_url" class="user-avatar" />
                  <span>{{ comment.username }}</span>
                </div>
              </td>
              <td>
                <span class="album-title">{{ comment.album_title || '-' }}</span>
              </td>
              <td>
                <span class="comment-content">{{ truncate(comment.content, 50) }}</span>
              </td>
              <td>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
              </td>
              <td>
                <button class="btn-action btn-delete" @click="handleDelete(comment)">
                  <i class="fas fa-trash"></i>
                </button>
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
          @click="currentPage--; loadComments()"
        >上一页</button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button
          class="page-btn"
          :disabled="currentPage >= totalPages"
          @click="currentPage++; loadComments()"
        >下一页</button>
      </div>
    </template>
  </div>
</template>

<script>
import { getAdminComments, deleteComment } from '../../api/admin.js';
import LoadingSpinner from '../../components/atoms/LoadingSpinner.vue';

export default {
  name: 'AdminCommentList',
  components: { LoadingSpinner },
  data() {
    return {
      comments: [],
      loading: true,
      currentPage: 1,
      pageSize: 20,
      totalComments: 0
    };
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalComments / this.pageSize);
    }
  },
  async mounted() {
    await this.loadComments();
  },
  methods: {
    async loadComments() {
      this.loading = true;
      try {
        const result = await getAdminComments({
          page: this.currentPage,
          page_size: this.pageSize
        });
        // 兼容 { data, total } 和直接数组两种响应格式
        this.comments = result.data || result || [];
        this.totalComments = result.total || this.comments.length;
      } catch (e) {
        console.error('加载评论失败:', e);
      } finally {
        this.loading = false;
      }
    },
    async handleDelete(comment) {
      if (!confirm('确定删除这条评论？')) return;
      try {
        await deleteComment(comment.comment_id);
        await this.loadComments();
      } catch (e) {
        console.error('删除失败:', e);
        alert('删除失败');
      }
    },
    truncate(text, len) {
      if (!text) return '';
      return text.length > len ? text.slice(0, len) + '...' : text;
    },
    formatDate(date) {
      if (!date) return '-';
      return new Date(date).toLocaleDateString('zh-CN');
    }
  }
};
</script>

<style scoped>
.comment-list-page {
  max-width: 1200px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xl);
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

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.user-avatar {
  width: 28px;
  height: 28px;
  object-fit: cover;
}

.album-title {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.comment-content {
  font-size: 0.85rem;
  color: var(--color-text-primary);
}

.comment-date {
  font-size: 0.8rem;
  color: var(--color-text-dim);
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
}

.page-btn:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.page-btn:disabled {
  opacity: 0.5;
}

.page-info {
  font-size: 0.9rem;
  color: var(--color-text-muted);
}
</style>
