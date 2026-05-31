<template>
  <div class="labels-page container-wide">
    <div class="page-header">
      <h1 class="page-title">社团</h1>
      <p class="page-subtitle">发现独立电子音乐厂牌与创作团体</p>
    </div>

    <LoadingSpinner v-if="loading" />

    <div v-else class="circles-grid">
      <CircleCard
        v-for="circle in circles"
        :key="circle.circle_id"
        :circle="circle"
        :is-followed="followedIds.has(circle.circle_id)"
        @circle-click="goToCircleById(circle.circle_id)"
        @tag-click="goToTag"
        @album-click="goToAlbum"
        @toggle-follow="toggleFollow"
      />
    </div>
  </div>
</template>

<script>
import { fetchCircles, checkCircleFollow, followCircle, unfollowCircle } from '../api';
import { useUserStore } from '../stores/user.js';
import { useNavigation } from '../composables/navigation.js';
import { useAuthGuard } from '../composables/authGuard.js';
import LoadingSpinner from '../components/atoms/LoadingSpinner.vue';
import CircleCard from '../components/molecules/CircleCard.vue';

export default {
  name: 'LabelsView',
  components: { LoadingSpinner, CircleCard },
  data() {
    return { circles: [], loading: true, followedIds: new Set() };
  },
  setup() {
    const userStore = useUserStore();
    const { goToAlbum, goToCircleById, goToTag } = useNavigation();
    const { guard } = useAuthGuard();
    return { userStore, goToAlbum, goToCircleById, goToTag, guard };
  },
  async mounted() {
    try {
      const result = await fetchCircles();
      this.circles = result.data;
      if (this.userStore.isLoggedIn) {
        for (const c of this.circles) {
          try {
            const data = await checkCircleFollow(c.circle_id);
            if (data.followed) this.followedIds.add(c.circle_id);
          } catch { /* ignore */ }
        }
        this.followedIds = new Set(this.followedIds);
      }
    } catch (e) {
      console.error('加载社团列表失败:', e);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    async toggleFollow(circle) {
      await this.guard(async () => {
        if (this.followedIds.has(circle.circle_id)) {
          await unfollowCircle(circle.circle_id);
          this.followedIds.delete(circle.circle_id);
        } else {
          await followCircle(circle.circle_id);
          this.followedIds.add(circle.circle_id);
        }
        this.followedIds = new Set(this.followedIds);
      }, () => alert('请先登录'));
    }
  }
};
</script>

<style scoped>
.labels-page {
  padding-top: var(--spacing-xl);
  padding-bottom: var(--spacing-2xl);
  position: relative;
  background-image: radial-gradient(rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 24px 24px;
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
  letter-spacing: -0.3px;
}

.page-subtitle {
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.circles-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-xl);
}

@media (max-width: 768px) {
  .circles-grid {
    grid-template-columns: 1fr;
  }
}
</style>
