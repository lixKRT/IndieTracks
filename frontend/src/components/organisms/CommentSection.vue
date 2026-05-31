<!-- 评论区（有机体） -->
<template>
  <div class="comment-section">
    <h3 class="comment-title">评论 ({{ total }})</h3>

    <div v-if="comments.length === 0" class="comment-empty">暂无评论</div>

    <div class="comment-list" ref="commentList">
      <CommentItem v-for="c in comments" :key="c.comment_id" :comment="c" />
    </div>

    <button
      v-if="comments.length < total"
      class="comment-load-more"
      @click="$emit('load-more')"
      :disabled="loading"
    >{{ loading ? '加载中...' : '加载更多' }}</button>

    <div class="comment-form" v-if="showForm">
      <textarea v-model="newComment" placeholder="写下你的想法..." rows="3" class="comment-textarea"></textarea>
      <button class="comment-submit" @click="submitComment" :disabled="!newComment.trim()">发表评论</button>
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
    showForm: { type: Boolean, default: true }
  },
  emits: ['add-comment', 'load-more'],
  data() {
    return { newComment: '' };
  },
  methods: {
    submitComment() {
      if (!this.newComment.trim()) return;
      this.$emit('add-comment', this.newComment.trim());
      this.newComment = '';
    }
  }
};
</script>

<style scoped>
.comment-section {
  margin-top: var(--spacing-xl);
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}
.comment-title { font-size: 1.1rem; color: var(--color-text-primary); margin-bottom: var(--spacing-md); }
.comment-empty { color: var(--color-text-dim); padding: var(--spacing-xl) 0; text-align: center; }

.comment-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--color-border) transparent;
}
.comment-list::-webkit-scrollbar { width: 4px; }
.comment-list::-webkit-scrollbar-track { background: transparent; }
.comment-list::-webkit-scrollbar-thumb { background: var(--color-border); }

.comment-load-more {
  display: block;
  width: 100%;
  margin-top: var(--spacing-sm);
  padding: 0.5rem;
  background: none;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.comment-load-more:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
}
.comment-load-more:disabled {
  opacity: 0.5;
  cursor: default;
}

.comment-form { margin-top: var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-sm); }
.comment-textarea { background: var(--color-bg-tertiary); border: 1px solid var(--color-border-light); color: var(--color-text-primary); font-size: 0.9rem; padding: var(--spacing-sm); resize: vertical; font-family: inherit; }
.comment-textarea:focus { outline: none; border-color: var(--color-accent); }
.comment-submit { align-self: flex-end; background: var(--color-accent); color: var(--color-text-primary); border: none; padding: 0.5rem 1.5rem; font-size: 0.85rem; cursor: pointer; transition: background var(--transition-fast); }
.comment-submit:hover:not(:disabled) { background: var(--color-accent-hover); }
.comment-submit:disabled { opacity: 0.4; cursor: default; }
</style>
