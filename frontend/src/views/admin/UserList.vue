<template>
  <div class="user-list-page">
    <h1 class="page-title">用户管理</h1>
    <p class="page-subtitle">仅管理员可访问</p>
    <!-- TODO: 实现用户列表 -->
  </div>
</template>

<script>
export default {
  name: 'AdminUserList'
};
</script>

<style scoped>
.user-list-page {
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
