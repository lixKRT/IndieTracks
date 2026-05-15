<!-- 评论区（有机体） -->
<template>
  <div class="comment-section">
    <h3 class="comment-title">评论 ({{ comments.length }})</h3>

    <div v-if="comments.length === 0" class="comment-empty">暂无评论</div>

    <CommentItem v-for="c in comments" :key="c.comment_id" :comment="c" />

    <div class="comment-form">
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
  props: { comments: { type: Array, default: () => [] } },
  emits: ['add-comment'],
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
.comment-section { margin-top: var(--spacing-xl); }
.comment-title { font-size: 1.1rem; color: var(--color-text-primary); margin-bottom: var(--spacing-md); }
.comment-empty { color: var(--color-text-dim); padding: var(--spacing-xl) 0; text-align: center; }

.comment-form { margin-top: var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-sm); }
.comment-textarea { background: var(--color-bg-tertiary); border: 1px solid var(--color-border-light); color: var(--color-text-primary); font-size: 0.9rem; padding: var(--spacing-sm); resize: vertical; font-family: inherit; }
.comment-textarea:focus { outline: none; border-color: var(--color-accent); }
.comment-submit { align-self: flex-end; background: var(--color-accent); color: var(--color-text-primary); border: none; padding: 0.5rem 1.5rem; font-size: 0.85rem; cursor: pointer; transition: background var(--transition-fast); }
.comment-submit:hover:not(:disabled) { background: var(--color-accent-hover); }
.comment-submit:disabled { opacity: 0.4; cursor: default; }
</style>
