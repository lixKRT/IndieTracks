<template>
  <div class="circle-card" @click="$emit('click', circle)">
    <div class="circle-avatar">
      <img :src="circle.logo_url" :alt="circle.name" class="circle-logo">
    </div>
    <div class="circle-info">
      <h3 class="circle-name">{{ circle.name }}</h3>
      <p class="circle-desc">{{ circle.description }}</p>
      
      <!-- 标签区域：阻止点击冒泡到卡片，独立处理标签跳转 -->
      <div class="circle-tags" v-if="circle.representative_tags && circle.representative_tags.length">
        <span
          v-for="tag in circle.representative_tags"
          :key="tag"
          class="tag"
          @click.stop="$emit('tag-click', tag)"
        >#{{ tag }}</span>
      </div>

      <div class="circle-stats">
        <div class="stat-item">
          <i class="fas fa-compact-disc"></i>
          <span>{{ circle.album_count }} 张专辑</span>
        </div>
        <div class="stat-item">
          <i class="fas fa-users"></i>
          <span>{{ circle.member_count }} 名成员</span>
        </div>
        <div v-if="circle.latest_album_date" class="stat-item">
          <i class="fas fa-calendar-alt"></i>
          <span>最新发行: {{ circle.latest_album_date }}</span>
        </div>
      </div>

      <button class="circle-action" @click.stop="$emit('click', circle)">查看社团 →</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CircleCard',
  props: { circle: { type: Object, required: true } },
  emits: ['click', 'tag-click']
};
</script>

<style scoped>
.circle-card {
  display: flex;
  gap: var(--spacing-xl);
  padding: var(--spacing-xl);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.circle-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 30px rgba(0, 0, 0, 0.3);
  border-color: var(--color-accent);
}

.circle-avatar {
  flex-shrink: 0;
  width: 140px;
  height: 140px;
  overflow: hidden;
  background: var(--color-bg-tertiary);
}

.circle-logo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.circle-card:hover .circle-logo {
  transform: scale(1.05);
}

.circle-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.circle-name {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
  transition: color 0.2s;
}

.circle-card:hover .circle-name {
  color: var(--color-accent);
}

.circle-desc {
  font-size: 0.95rem;
  color: var(--color-text-muted);
  line-height: 1.5;
  margin-bottom: var(--spacing-xs);
}

.circle-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: var(--spacing-xs) 0;
}

.tag {
  background: rgba(255, 107, 107, 0.15);
  color: var(--color-accent);
  font-size: 0.75rem;
  padding: 0.2rem 0.7rem;
  border-radius: 0;
  letter-spacing: 0.3px;
  cursor: pointer;
  transition: background 0.2s;
}

.tag:hover {
  background: rgba(255, 107, 107, 0.3);
}

.circle-stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-xs);
  font-size: 0.85rem;
  color: var(--color-text-dim);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat-item i {
  width: 18px;
  color: var(--color-accent);
}

.circle-action {
  align-self: flex-start;
  margin-top: var(--spacing-sm);
  background: transparent;
  border: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
  padding: 0.5rem 1.2rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.circle-action:hover {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: var(--color-bg-primary);
}

/* 响应式：平板以下调整 */
@media (max-width: 768px) {
  .circle-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .circle-avatar {
    width: 120px;
    height: 120px;
  }
  .circle-stats {
    justify-content: center;
  }
  .circle-action {
    align-self: center;
  }
  .circle-tags {
    justify-content: center;
  }
}
</style>