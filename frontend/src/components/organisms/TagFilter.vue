<!-- 标签筛选器（有机体） -->
<template>
  <div class="tag-filter">
    <div class="filter-tags">
      <span
        class="filter-tag"
        :class="{ active: !selectedTag }"
        @click="$emit('update:tag', '')"
      >全部</span>
      <span
        v-for="t in tags"
        :key="t.tag_id"
        class="filter-tag"
        :class="{ active: selectedTag === t.name }"
        @click="$emit('update:tag', t.name)"
      >{{ t.name }}</span>
    </div>
    <div class="filter-price">
      <span class="filter-label">价格：</span>
      <span class="filter-option" :class="{ active: selectedPrice === '' }" @click="$emit('update:price', '')">全部</span>
      <span class="filter-option" :class="{ active: selectedPrice === 'free' }" @click="$emit('update:price', 'free')">免费</span>
      <span class="filter-option" :class="{ active: selectedPrice === 'paid' }" @click="$emit('update:price', 'paid')">付费</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TagFilter',
  props: {
    tags: { type: Array, default: () => [] },
    selectedTag: { type: String, default: '' },
    selectedPrice: { type: String, default: '' }
  },
  emits: ['update:tag', 'update:price']
};
</script>

<style scoped>
.tag-filter { margin-bottom: var(--spacing-xl); }

.filter-tags { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: var(--spacing-md); }
.filter-tag {
  font-size: 0.8rem; color: var(--color-text-muted);
  background: rgba(255,255,255,0.04);
  border: 1px solid transparent;
  padding: 0.3rem 0.8rem; cursor: pointer;
  transition: all var(--transition-fast);
}
.filter-tag:hover { color: var(--color-accent); border-color: var(--color-border); }
.filter-tag.active { color: var(--color-accent); background: rgba(255,107,107,0.1); border-color: var(--color-accent); }

.filter-price { display: flex; align-items: center; gap: var(--spacing-sm); }
.filter-label { font-size: 0.8rem; color: var(--color-text-dim); }
.filter-option {
  font-size: 0.8rem; color: var(--color-text-muted); cursor: pointer;
  padding: 0.15rem 0.6rem; transition: color var(--transition-fast);
}
.filter-option:hover { color: var(--color-accent); }
.filter-option.active { color: var(--color-accent); font-weight: 600; }
</style>
