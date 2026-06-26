<!-- 评论区（有机体） -->
<template>
  <div class="comment-section">
    <h3 class="comment-title">评论 ({{ total }})</h3>

    <!-- 已登录显示评论框，未登录提示登录 -->
    <div class="comment-form" v-if="isLoggedIn">
      <textarea v-model="newComment" placeholder="写下你的想法..." rows="2" class="comment-textarea"></textarea>
      <button class="comment-submit" @click="submitComment" :disabled="!newComment.trim()">发表评论</button>
    </div>
    <p v-else class="login-hint">登录后可以发表评论</p>

    <div v-if="comments.length === 0" class="comment-empty">暂无评论</div>

    <div class="comment-list" ref="commentList" @scroll="handleScroll">
      <!-- 只有评论作者才能编辑/删除 -->
      <CommentItem
        v-for="c in comments"
        :key="c.comment_id"
        :comment="c"
        :can-edit="userId === c.user_id"
        @edit="handleEdit"
        @delete="handleDelete"
      />
      <div v-if="loading" class="loading-hint">加载中...</div>
    </div>
  </div>
</template>

<script>
import CommentItem from '../molecules/CommentItem.vue';

export default {
  name: 'CommentSection',
  components: { CommentItem },
  props: {
    comments: { type: Array, default: () => [] },
    total: { type: Number, default: 0 },
    loading: { type: Boolean, default: false },
    isLoggedIn: { type: Boolean, default: false },
    userId: { type: Number, default: null }
  },
  emits: ['load-more', 'add-comment', 'edit-comment', 'delete-comment'],
  data() {
    return { newComment: '' };
  },
  methods: {
    submitComment() {
      if (!this.newComment.trim()) return;
      this.$emit('add-comment', this.newComment.trim());
      this.newComment = '';
    },
    handleEdit(comment) {
      this.$emit('edit-comment', comment);
    },
    handleDelete(commentId) {
      this.$emit('delete-comment', commentId);
    },
    // 无限滚动：滚动到距底部 20px 时触发加载更多
    handleScroll() {
      const el = this.$refs.commentList;
      if (!el || this.loading) return;
      if (el.scrollTop + el.clientHeight >= el.scrollHeight - 20) {
        if (this.comments.length < this.total) {
          this.$emit('load-more');
        }
      }
    }
  }
};
</script>

<style scoped>
.comment-section {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}
.comment-title { font-size: 1.1rem; color: var(--color-text-primary); margin-bottom: var(--spacing-sm); }
.comment-empty { color: var(--color-text-dim); padding: var(--spacing-lg) 0; text-align: center; font-size: 0.85rem; }

.comment-form { display: flex; flex-direction: column; gap: var(--spacing-xs); margin-bottom: var(--spacing-sm); }
.comment-textarea { background: var(--color-bg-tertiary); border: 1px solid var(--color-border-light); color: var(--color-text-primary); font-size: 0.85rem; padding: 0.4rem; resize: none; font-family: inherit; }
.comment-textarea:focus { outline: none; border-color: var(--color-accent); }
.comment-submit { align-self: flex-end; background: var(--color-accent); color: var(--color-text-primary); border: none; padding: 0.3rem 1rem; font-size: 0.8rem; cursor: pointer; transition: background var(--transition-fast); }
.comment-submit:hover:not(:disabled) { background: var(--color-accent-hover); }
.comment-submit:disabled { opacity: 0.4; cursor: default; }

.login-hint { color: var(--color-text-dim); font-size: 0.8rem; margin-bottom: var(--spacing-sm); }

.comment-list {
  height: 400px; /* 固定高度以支持滚动加载 */
  overflow-y: auto;
  scrollbar-width: thin; /* Firefox 细滚动条 */
  scrollbar-color: var(--color-border) transparent;
}
.comment-list::-webkit-scrollbar { width: 4px; }
.comment-list::-webkit-scrollbar-track { background: transparent; }
.comment-list::-webkit-scrollbar-thumb { background: var(--color-border); }

.loading-hint { text-align: center; color: var(--color-text-dim); font-size: 0.8rem; padding: var(--spacing-sm) 0; }
</style>
