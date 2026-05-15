<!-- 评论条目（分子） -->
<template>
  <div class="comment-item">
    <img :src="comment.avatar_url" :alt="comment.username" class="comment-avatar">
    <div class="comment-body">
      <div class="comment-header">
        <span class="comment-username">{{ comment.username }}</span>
        <span class="comment-time">{{ comment.created_at }}</span>
      </div>
      <p class="comment-content">{{ comment.content }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CommentItem',
  props: { comment: { type: Object, required: true } }
};
</script>

<style scoped>
.comment-item { display: flex; gap: var(--spacing-md); padding: var(--spacing-md) 0; border-bottom: 1px solid var(--color-border); }
.comment-avatar { width: 40px; height: 40px; border-radius: 0; object-fit: cover; flex-shrink: 0; background: var(--color-bg-tertiary); }
.comment-body { flex: 1; min-width: 0; }
.comment-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: var(--spacing-xs); }
.comment-username { font-size: 0.85rem; font-weight: 600; color: var(--color-text-primary); }
.comment-time { font-size: 0.75rem; color: var(--color-text-dim); }
.comment-content { font-size: 0.85rem; color: var(--color-text-muted); line-height: 1.6; }
</style>
