<!-- 评论条目（分子） -->
<template>
  <div class="comment-item">
    <router-link v-if="comment.user_id" :to="`/user/${comment.user_id}`" class="comment-avatar-link">
      <img :src="comment.avatar_url" :alt="comment.username" class="comment-avatar">
    </router-link>
    <img v-else :src="comment.avatar_url" :alt="comment.username" class="comment-avatar">
    <div class="comment-body">
      <div class="comment-header">
        <router-link v-if="comment.user_id" :to="`/user/${comment.user_id}`" class="comment-username">{{ comment.username }}</router-link>
        <span v-else class="comment-username">{{ comment.username }}</span>
        <div class="comment-actions" v-if="canEdit">
          <button class="action-btn" @click="$emit('edit', comment)" title="编辑"><i class="fas fa-edit"></i></button>
          <button class="action-btn delete" @click="$emit('delete', comment.comment_id)" title="删除"><i class="fas fa-trash"></i></button>
        </div>
      </div>
      <p class="comment-content">{{ comment.content }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CommentItem',
  props: {
    comment: { type: Object, required: true },
    canEdit: { type: Boolean, default: false }
  },
  emits: ['edit', 'delete']
};
</script>

<style scoped>
.comment-item { display: flex; gap: var(--spacing-md); padding: var(--spacing-md) 0; border-bottom: 1px solid var(--color-border); }
.comment-avatar-link { flex-shrink: 0; }
.comment-avatar { width: 40px; height: 40px; border-radius: 0; object-fit: cover; flex-shrink: 0; background: var(--color-bg-tertiary); display: block; }
.comment-body { flex: 1; min-width: 0; }
.comment-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: var(--spacing-xs); }
.comment-username { font-size: 0.85rem; font-weight: 600; color: var(--color-text-primary); text-decoration: none; transition: color 0.2s; }
.comment-username:hover { color: var(--color-accent); }
.comment-actions { display: flex; gap: 0.3rem; }
.action-btn { background: none; border: none; color: var(--color-text-dim); font-size: 0.75rem; cursor: pointer; padding: 0.2rem; transition: color 0.2s; }
.action-btn:hover { color: var(--color-accent); }
.action-btn.delete:hover { color: #ff4444; }
.comment-content { font-size: 0.85rem; color: var(--color-text-muted); line-height: 1.6; }
</style>
