<!-- 空状态（原子） -->
<template>
  <div class="empty-state">
    <p>{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    message: { type: String, default: '暂无数据' }
  }
};
</script>
