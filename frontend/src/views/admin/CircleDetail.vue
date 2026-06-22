<template>
  <div class="circle-detail-page">
    <h1 class="page-title">社团详情</h1>
    <p class="page-subtitle">仅管理员可访问</p>
    <!-- TODO: 实现社团详情和成员管理 -->
  </div>
</template>

<script>
export default {
  name: 'AdminCircleDetail'
};
</script>

<style scoped>
.circle-detail-page {
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
