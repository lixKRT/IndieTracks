<!-- 社团卡片（分子） -->
<template>
  <div class="circle-card" @click="$emit('click', circle)">
    <img :src="circle.logo_url" :alt="circle.name" class="circle-logo">
    <div class="circle-info">
      <h3 class="circle-name">{{ circle.name }}</h3>
      <p class="circle-desc">{{ circle.description }}</p>
      <div class="circle-stats">
        <span>{{ circle.album_count }} 张专辑</span>
        <span>{{ circle.member_count }} 名成员</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CircleCard',
  props: { circle: { type: Object, required: true } },
  emits: ['click']
};
</script>

<style scoped>
.circle-card {
  display: flex;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
}
.circle-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.3); }

.circle-logo { width: 80px; height: 80px; object-fit: cover; flex-shrink: 0; }
.circle-info { flex: 1; min-width: 0; }
.circle-name { font-size: 1.1rem; color: var(--color-text-primary); margin-bottom: var(--spacing-xs); }
.circle-desc { font-size: 0.85rem; color: var(--color-text-muted); line-height: 1.5; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; margin-bottom: var(--spacing-sm); }
.circle-stats { display: flex; gap: var(--spacing-lg); font-size: 0.8rem; color: var(--color-text-dim); }
</style>
