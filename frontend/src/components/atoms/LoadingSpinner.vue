<!-- LoadingSpinner — 加载中占位原子组件 -->
<!-- 样式定义在全局 utilities.css，无 scoped 样式 -->
<template>
  <div class="loading-container">
    <div class="loading-spinner"></div>
    <p>{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    message: { type: String, default: '加载中...' }
  }
};
</script>
