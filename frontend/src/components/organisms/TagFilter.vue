<!-- TagFilter — 标签 + 价格筛选器，emit update:tag / update:price 配合父组件 v-model 使用 -->
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
    <!-- 价格筛选使用语义字符串：'' 全部 / 'free' 免费 / 'paid' 付费 -->
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
  // update:tag / update:price 遵循 Vue v-model 命名约定，父组件可直接 v-model:tag="xxx"
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
.filter-tag.active { color: var(--color-accent); background: rgba(255,107,107,0.1); border-color: var(--color-accent); } /* 选中态：accent 色文字 + 半透明背景 + 边框 */

.filter-price { display: flex; align-items: center; gap: var(--spacing-sm); }
.filter-label { font-size: 0.8rem; color: var(--color-text-dim); }
.filter-option {
  font-size: 0.8rem; color: var(--color-text-muted); cursor: pointer;
  padding: 0.15rem 0.6rem; transition: color var(--transition-fast);
}
.filter-option:hover { color: var(--color-accent); }
.filter-option.active { color: var(--color-accent); font-weight: 600; }
</style>
