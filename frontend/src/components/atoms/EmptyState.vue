<!-- EmptyState — 空状态占位原子组件，列表/搜索无结果时展示 -->
<template>
  <div class="empty-state">
    <p>{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    // 空状态提示文案，父组件可自定义
    message: { type: String, default: '暂无数据' }
  }
};
</script>
