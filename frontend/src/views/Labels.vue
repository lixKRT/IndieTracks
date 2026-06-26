<template>
  <div class="labels-page container-wide">
    <div class="page-header">
      <h1 class="page-title">社团</h1>
      <p class="page-subtitle">发现独立电子音乐厂牌与创作团体</p>
    </div>

    <LoadingSpinner v-if="loading" />

    <template v-else>
      <div class="circles-grid">
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

      <!-- 加载更多 -->
      <div class="load-more-wrap" v-if="circles.length < totalCircles">
        <button
          class="load-more-btn"
          :disabled="loadingMore"
          @click="loadMore"
        >
          {{ loadingMore ? '加载中...' : '加载更多' }}
        </button>
      </div>
    </template>
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
    return {
      circles: [],
      loading: true,
      loadingMore: false,
      page: 1,
      pageSize: 12,
      totalCircles: 0,
      // 需整体替换 Set 才能触发 Vue 响应式更新（Options API 下 Set 变更不可追踪）
      followedIds: new Set()
    };
  },
  setup() {
    const userStore = useUserStore();
    const { goToAlbum, goToCircleById, goToTag } = useNavigation();
    const { guard } = useAuthGuard(); // 未登录时弹窗提示，不跳转
    return { userStore, goToAlbum, goToCircleById, goToTag, guard };
  },
  async mounted() {
    await this.loadData();
  },
  methods: {
    async loadData() {
      this.loading = true;
      try {
        const result = await fetchCircles({ page: 1, page_size: this.pageSize });
        this.circles = result.data;
        this.totalCircles = result.total;
        this.page = 1;

        if (this.userStore.isLoggedIn) {
          await this.checkFollowStatus(this.circles);
        }
      } catch (e) {
        console.error('加载社团列表失败:', e);
      } finally {
        this.loading = false;
      }
    },
    async loadMore() {
      if (this.loadingMore || this.circles.length >= this.totalCircles) return;
      this.loadingMore = true;
      try {
        this.page++;
        const result = await fetchCircles({ page: this.page, page_size: this.pageSize });
        this.circles.push(...result.data);

        if (this.userStore.isLoggedIn) {
          await this.checkFollowStatus(result.data);
        }
      } catch (e) {
        console.error('加载更多失败:', e);
        this.page--;
      } finally {
        this.loadingMore = false;
      }
    },
    async checkFollowStatus(circles) {
      for (const c of circles) {
        try {
          const data = await checkCircleFollow(c.circle_id);
          if (data.followed) this.followedIds.add(c.circle_id);
        } catch { /* ignore */ }
      }
      this.followedIds = new Set(this.followedIds); // 重新赋值触发响应式
    },
    async toggleFollow(circle) {
      await this.guard(async () => {
        if (this.followedIds.has(circle.circle_id)) {
          await unfollowCircle(circle.circle_id);
          this.followedIds.delete(circle.circle_id);
        } else {
          await followCircle(circle.circle_id);
          this.followedIds.add(circle.circle_id);
        }
        this.followedIds = new Set(this.followedIds); // 重新赋值触发响应式
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
  /* 点阵装饰背景，增强页面质感 */
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

.load-more-wrap {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-2xl);
}

.load-more-btn {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  padding: 12px 48px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-btn:hover:not(:disabled) {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .circles-grid {
    grid-template-columns: 1fr;
  }
}
</style>
