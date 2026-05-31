<!-- 加载中 spinner（原子） -->
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
