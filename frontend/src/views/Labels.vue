<!-- 社团列表页 -->
<template>
  <div class="labels-page container">
    <h1 class="page-title">社团</h1>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else class="circle-list">
      <CircleCard
        v-for="c in circles"
        :key="c.circle_id"
        :circle="c"
        @click="goToCircle(c)"
      />
    </div>
  </div>
</template>

<script>
import CircleCard from '../components/molecules/CircleCard.vue';
import { fetchCircles } from '../api/mock.js';

export default {
  name: 'LabelsView',
  components: { CircleCard },
  data() {
    return { circles: [], loading: true };
  },
  async mounted() {
    try {
      const result = await fetchCircles();
      this.circles = result.data;
    } catch (e) {
      console.error('加载社团列表失败:', e);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    goToCircle(c) { this.$router.push(`/label/${c.circle_id}`); }
  }
};
</script>

<style scoped>
.labels-page { padding-top: var(--spacing-xl); }
.page-title { font-size: 1.8rem; color: var(--color-text-primary); margin-bottom: var(--spacing-xl); }
.circle-list { display: flex; flex-direction: column; gap: var(--spacing-md); }
</style>
