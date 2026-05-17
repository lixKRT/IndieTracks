<template>
  <div class="labels-page container-wide">
    <div class="page-header">
      <h1 class="page-title">社团</h1>
      <p class="page-subtitle">发现独立电子音乐厂牌与创作团体</p>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else class="circle-grid">
      <CircleCard
        v-for="c in circles"
        :key="c.circle_id"
        :circle="c"
        @click="goToCircle(c)"
        @tag-click="goToTag"
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
    goToCircle(c) {
      this.$router.push(`/label/${c.circle_id}`);
    },
    goToTag(tag) {
      this.$router.push({ path: '/tag', query: { tag } });
    }
  }
};
</script>

<style scoped>
.labels-page {
  padding-top: var(--spacing-xl);
  padding-bottom: var(--spacing-2xl);
}

.page-header {
  margin-bottom: var(--spacing-xl);
  text-align: center;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

.page-subtitle {
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

/* 桌面端单列布局，每个卡片占满宽度 */
.circle-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
  max-width: 1000px;
  margin: 0 auto; /* 可选居中，让卡片不占满全屏太宽 */
}

/* 如果希望占满全屏更宽，可以去掉 max-width */
@media (max-width: 768px) {
  .circle-grid {
    gap: var(--spacing-lg);
  }
}
</style>