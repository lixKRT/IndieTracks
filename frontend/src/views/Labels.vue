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

    <div v-else class="circles-grid">
      <div
        v-for="circle in circles"
        :key="circle.circle_id"
        class="circle-card"
      >
        <div class="circle-info" @click="goToCircle(circle)">
          <div class="circle-logo">
            <img :src="circle.logo_url" :alt="circle.name">
          </div>
          <div class="circle-details">
            <h2 class="circle-name">{{ circle.name }}</h2>
            <p class="circle-desc">{{ circle.description }}</p>
            <div class="circle-tags" v-if="circle.representative_tags.length">
              <span
                v-for="tag in circle.representative_tags"
                :key="tag"
                class="tag"
                @click.stop="goToTag(tag)"
              >#{{ tag }}</span>
            </div>
            <div class="circle-stats">
              <span><i class="fas fa-compact-disc"></i> {{ circle.album_count }} 张专辑</span>
              <span><i class="fas fa-users"></i> {{ circle.member_count }} 名成员</span>
            </div>
          </div>
        </div>

        <div class="albums-stack" v-if="circle.preview_albums && circle.preview_albums.length">
          <div
            v-for="(album, idx) in circle.preview_albums"
            :key="album.album_id"
            class="stack-item"
            :style="getStackStyle(idx, circle.preview_albums.length)"
            @click.stop="goToAlbum(album)"
          >
            <div class="stack-cover">
              <img :src="album.cover_url" :alt="album.title">
            </div>
            <div class="stack-caption">
              <div class="stack-title">{{ album.title }}</div>
              <div class="stack-tags">
                <span v-for="t in album.tags.slice(0, 1)" :key="t">#{{ t }}</span>
              </div>
            </div>
          </div>
          <div
            v-if="circle.album_count > 4"
            class="stack-more"
            @click.stop="goToCircle(circle)"
          >
            <span>+{{ circle.album_count - 4 }}</span>
            <i class="fas fa-arrow-right"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { fetchCircles } from '../api/mock.js';

export default {
  name: 'LabelsView',
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
    goToCircle(circle) {
      this.$router.push(`/label/${circle.circle_id}`);
    },
    goToAlbum(album) {
      this.$router.push(`/album/${album.album_id}`);
    },
    goToTag(tag) {
      this.$router.push({ path: '/tag', query: { tag } });
    },
    getStackStyle(index, total) {
      const angle = (index - (total - 1) / 2) * 2.5;
      const offsetX = (index - (total - 1) / 2) * 4;
      const zIndex = total - index;
      return {
        transform: `rotate(${angle}deg) translateX(${offsetX}px)`,
        zIndex: zIndex,
        marginRight: index === total - 1 ? '0' : '-12px'
      };
    }
  }
};
</script>

<style scoped>
.labels-page {
  padding-top: var(--spacing-xl);
  padding-bottom: var(--spacing-2xl);
  position: relative;
  /* 细微点阵纹理，增强暗黑质感 */
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

.circle-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  transition: transform 0.3s cubic-bezier(0.2, 0, 0, 1), box-shadow 0.3s ease, border-color 0.2s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.circle-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 18px 28px -8px rgba(0, 0, 0, 0.4);
  border-color: var(--color-accent);
}

.circle-info {
  padding: var(--spacing-lg);
  cursor: pointer;
  display: flex;
  gap: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  transition: background 0.2s;
}

.circle-info:hover {
  background: rgba(255, 107, 107, 0.02);
}

.circle-logo {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  overflow: hidden;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: 2px;
  transition: transform 0.2s;
}

.circle-card:hover .circle-logo {
  transform: scale(1.02);
}

.circle-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.circle-details {
  flex: 1;
  min-width: 0;
}

.circle-name {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 0.4rem;
  line-height: 1.3;
  letter-spacing: -0.2px;
}

.circle-desc {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  line-height: 1.45;
  margin-bottom: 0.6rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.circle-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 0.6rem;
}

.tag {
  background: linear-gradient(135deg, rgba(255,107,107,0.12), rgba(255,107,107,0.05));
  color: var(--color-accent);
  font-size: 0.7rem;
  padding: 0.2rem 0.6rem;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 2px;
  font-weight: 500;
}

.tag:hover {
  background: rgba(255,107,107,0.25);
  transform: translateY(-1px);
}

.circle-stats {
  display: flex;
  gap: var(--spacing-md);
  font-size: 0.7rem;
  color: var(--color-text-dim);
}

.circle-stats i {
  margin-right: 0.25rem;
  width: 14px;
  color: var(--color-accent);
}

.albums-stack {
  display: flex;
  align-items: flex-end;
  padding: var(--spacing-md) var(--spacing-lg) var(--spacing-lg);
  background: rgba(0, 0, 0, 0.25);
  overflow-x: auto;
  scrollbar-width: thin;
  gap: 2px;
  border-top: 1px solid var(--color-border);
}

.stack-item {
  flex-shrink: 0;
  width: 110px;
  transition: all 0.2s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-tertiary);
  border-radius: 4px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0,0,0,0.2);
  overflow: hidden;
}

.stack-item:hover {
  transform: translateY(-6px) rotate(0deg) !important;
  z-index: 10 !important;
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.4);
}

.stack-cover {
  width: 100%;
  aspect-ratio: 1 / 1;
  overflow: hidden;
}

.stack-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.2s;
}

.stack-item:hover .stack-cover img {
  transform: scale(1.03);
}

.stack-caption {
  padding: 8px 8px;
  background: var(--color-bg-secondary);
}

.stack-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 3px;
}

.stack-tags {
  font-size: 0.65rem;
  color: var(--color-accent);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}

.stack-tags span {
  background: none;
  padding: 0;
}

.stack-more {
  flex-shrink: 0;
  width: 110px;
  background: var(--color-bg-tertiary);
  border: 1px dashed var(--color-border);
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.25s;
  color: var(--color-text-muted);
  font-size: 1.3rem;
  font-weight: 600;
  aspect-ratio: 1 / 1;
  background: linear-gradient(145deg, #222, #1a1a1a);
}

.stack-more:hover {
  background: var(--color-accent);
  color: var(--color-bg-primary);
  border-color: var(--color-accent);
  transform: scale(0.98);
}

.stack-more i {
  font-size: 1rem;
  transition: transform 0.2s;
}

.stack-more:hover i {
  transform: translateX(3px);
}

/* 响应式微调 */
@media (max-width: 768px) {
  .circle-info {
    flex-direction: column;
    text-align: center;
  }
  .circle-logo {
    margin: 0 auto;
  }
  .stack-item,
  .stack-more {
    width: 90px;
  }
  .circle-name {
    font-size: 1.1rem;
  }
}
</style>