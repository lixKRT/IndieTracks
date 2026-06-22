<template>
  <div class="circle-list-page">
    <h1 class="page-title">社团管理</h1>
    <p class="page-subtitle">仅管理员可访问</p>
    <!-- TODO: 实现社团列表 -->
  </div>
</template>

<script>
export default {
  name: 'AdminCircleList'
};
</script>

<style scoped>
.circle-list-page {
  max-width: 1200px;
}
.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}
.page-subtitle {
  color: var(--color-text-muted);
}
</style>
