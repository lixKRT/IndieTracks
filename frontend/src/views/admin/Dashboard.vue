<!-- AdminDashboard — 管理后台数据概览，含统计卡片与排行榜 -->
<template>
  <div class="dashboard-page">
    <h1 class="page-title">数据透视</h1>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-compact-disc"></i></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalAlbums || 0 }}</span>
          <span class="stat-label">专辑总数</span>
        </div>
      </div>
      <!-- staff 角色专属：社团和用户统计仅管理员可见 -->
      <div class="stat-card" v-if="isStaff">
        <div class="stat-icon"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalCircles || 0 }}</span>
          <span class="stat-label">社团总数</span>
        </div>
      </div>
      <div class="stat-card" v-if="isStaff">
        <div class="stat-icon"><i class="fas fa-user"></i></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalUsers || 0 }}</span>
          <span class="stat-label">用户总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-comment"></i></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalComments || 0 }}</span>
          <span class="stat-label">评论总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><i class="fas fa-heart"></i></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalFavorites || 0 }}</span>
          <span class="stat-label">收藏总数</span>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 热门专辑排行 -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">热门专辑</h3>
          <div class="chart-actions">
            <button
              v-for="p in periods"
              :key="p.value"
              class="period-btn"
              :class="{ active: albumPeriod === p.value }"
              @click="albumPeriod = p.value; loadTopAlbums()"
            >{{ p.label }}</button>
          </div>
        </div>
        <div class="chart-content">
          <LoadingSpinner v-if="loadingAlbums" />
          <div v-else-if="topAlbums.length === 0" class="empty-state">暂无数据</div>
          <div v-else class="ranking-list">
            <div v-for="(album, index) in topAlbums" :key="album.album_id" class="ranking-item">
              <span class="ranking-index" :class="{ top3: index < 3 }">{{ index + 1 }}</span>
              <img :src="album.cover_url" :alt="album.title" class="ranking-cover" />
              <div class="ranking-info">
                <span class="ranking-name">{{ album.title }}</span>
                <span class="ranking-sub">{{ album.circle_name }}</span>
              </div>
              <span class="ranking-count">{{ album.favorite_count || 0 }} 收藏</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 活跃社团排行 -->
      <div class="chart-card" v-if="isStaff">
        <div class="chart-header">
          <h3 class="chart-title">活跃社团</h3>
          <div class="chart-actions">
            <button
              v-for="p in periods"
              :key="p.value"
              class="period-btn"
              :class="{ active: circlePeriod === p.value }"
              @click="circlePeriod = p.value; loadTopCircles()"
            >{{ p.label }}</button>
          </div>
        </div>
        <div class="chart-content">
          <LoadingSpinner v-if="loadingCircles" />
          <div v-else-if="topCircles.length === 0" class="empty-state">暂无数据</div>
          <div v-else class="ranking-list">
            <div v-for="(circle, index) in topCircles" :key="circle.circle_id" class="ranking-item">
              <span class="ranking-index" :class="{ top3: index < 3 }">{{ index + 1 }}</span>
              <img :src="circle.logo_url" :alt="circle.name" class="ranking-cover" />
              <div class="ranking-info">
                <span class="ranking-name">{{ circle.name }}</span>
                <span class="ranking-sub">{{ circle.member_count || 0 }} 成员</span>
              </div>
              <span class="ranking-count">{{ circle.album_count || 0 }} 专辑</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getDashboardStats, getTopAlbums, getTopCircles } from '../../api/admin.js';
import { useUserStore } from '../../stores/user.js';
import LoadingSpinner from '../../components/atoms/LoadingSpinner.vue';

export default {
  name: 'AdminDashboard',
  components: { LoadingSpinner },
  setup() {
    const userStore = useUserStore();
    return { userStore };
  },
  data() {
    return {
      stats: {},
      topAlbums: [],
      topCircles: [],
      albumPeriod: 'month',
      circlePeriod: 'month',
      loadingAlbums: false,
      loadingCircles: false,
      periods: [
        { value: 'week', label: '本周' },
        { value: 'month', label: '本月' },
        { value: 'all', label: '全部' }
      ]
    };
  },
  computed: {
    // staff = 管理员角色，控制部分统计卡片和活跃社团排行的可见性
    isStaff() {
      return this.userStore.user?.user_role === 'staff';
    }
  },
  async mounted() {
    await this.loadData();
  },
  methods: {
    async loadData() {
      try {
        this.stats = await getDashboardStats();
        await Promise.all([this.loadTopAlbums(), this.loadTopCircles()]);
      } catch (e) {
        console.error('加载数据失败:', e);
      }
    },
    async loadTopAlbums() {
      this.loadingAlbums = true;
      try {
        this.topAlbums = await getTopAlbums(this.albumPeriod, 50);
      } catch (e) {
        console.error('加载热门专辑失败:', e);
      } finally {
        this.loadingAlbums = false;
      }
    },
    async loadTopCircles() {
      if (!this.isStaff) return; // 非管理员不加载社团排行
      this.loadingCircles = true;
      try {
        this.topCircles = await getTopCircles(this.circlePeriod, 50);
      } catch (e) {
        console.error('加载活跃社团失败:', e);
      } finally {
        this.loadingCircles = false;
      }
    }
  }
};
</script>

<style scoped>
.dashboard-page {
  max-width: 1200px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xl);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 107, 107, 0.1); /* 项目 accent 色 (#ff6b6b) 10% 透明度 */
  color: var(--color-accent);
  font-size: 1.2rem;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

/* 图表区域 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--spacing-lg);
}

.chart-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.chart-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.chart-actions {
  display: flex;
  gap: var(--spacing-xs);
}

.period-btn {
  padding: 4px 10px;
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.period-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.period-btn.active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: var(--color-text-primary);
}

.chart-content {
  padding: var(--spacing-md);
  max-height: 500px;
  overflow-y: auto;
}

/* 排行榜 */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm);
  transition: background var(--transition-fast);
}

.ranking-item:hover {
  background: rgba(255, 255, 255, 0.03);
}

.ranking-index {
  width: 24px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-dim);
  text-align: center;
}

.ranking-index.top3 {
  color: var(--color-accent); /* 前三名高亮使用项目主色 */
}

.ranking-cover {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border: 1px solid var(--color-border);
}

.ranking-info {
  flex: 1;
  min-width: 0;
}

.ranking-name {
  display: block;
  font-size: 0.85rem;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ranking-sub {
  font-size: 0.75rem;
  color: var(--color-text-dim);
}

.ranking-count {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-xl);
  color: var(--color-text-dim);
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
