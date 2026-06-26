<!-- App — 根组件，仅挂载全局布局，所有页面内容由 MainLayout 内的 router-view 渲染 -->
<template>
  <MainLayout />
</template>

<script>
import MainLayout from './layouts/MainLayout.vue';

export default {
  name: 'App',
  components: { MainLayout }
};
</script>
