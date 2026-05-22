<template>
  <section class="hero">
    <div class="hero-content container-wide">
      <div class="hero-text">
        <h1 class="hero-title">
          <span class="wave-icon">🎵</span>
          {{ title }}
        </h1>
        <p class="hero-subtitle">
          {{ subtitle }}
        </p>
        <div class="hero-actions">
          <router-link :to="primaryAction.link" class="hero-btn primary">{{ primaryAction.text }}</router-link>
          <button class="hero-btn secondary" @click="handleSecondaryAction">{{ secondaryAction.text }}</button>
        </div>
      </div>
      <div class="hero-stats">
        <div v-for="(stat, index) in stats" :key="index" class="stat">
          <span class="stat-number">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </div>
    <div class="hero-wave"></div>
  </section>
</template>

<script>
export default {
  name: 'HeroSection',
  props: {
    title: {
      type: String,
      default: '发现独立电子音乐'
    },
    subtitle: {
      type: String,
      default: '探索来自世界各地创作者的声音，从东方同人到硬核电子，免费试听，支持你爱的音乐人。'
    },
    primaryAction: {
      type: Object,
      default: () => ({
        text: '浏览全部',
        link: '/tag'
      })
    },
    secondaryAction: {
      type: Object,
      default: () => ({
        text: '最新专辑 ↓',
        action: null
      })
    },
    stats: {
      type: Array,
      default: () => [
        { value: '0+', label: '张专辑' },
        { value: '0', label: '个社团' },
        { value: '100%', label: '免费试听' }
      ]
    }
  },
  emits: ['secondary-action-click'],
  methods: {
    handleSecondaryAction() {
      this.$emit('secondary-action-click');
    }
  }
};
</script>

<style scoped>
/* Hero 区域 */
.hero {
  position: relative;
  background: linear-gradient(135deg, #0e0e0e 0%, #1a1a1a 100%);
  border-bottom: 1px solid var(--color-border);
  padding: 4rem 0 5rem;
  overflow: hidden;
}

.hero-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-text {
  flex: 1;
  min-width: 280px;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1.2;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.wave-icon {
  display: inline-block;
  margin-right: 12px;
  filter: drop-shadow(0 0 6px var(--color-accent));
}

.hero-subtitle {
  font-size: 1.1rem;
  color: var(--color-text-muted);
  max-width: 500px;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.hero-btn {
  padding: 0.8rem 2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
  border: none;
  font-size: 0.9rem;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
}

.hero-btn.primary {
  background: var(--color-accent);
  color: var(--color-bg-primary);
}

.hero-btn.primary:hover {
  background: var(--color-accent-hover);
  transform: translateY(-2px);
}

.hero-btn.secondary {
  background: transparent;
  border: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
}

.hero-btn.secondary:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
  transform: translateY(-2px);
}

.hero-stats {
  display: flex;
  gap: 2rem;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(8px);
  padding: 1.5rem 2rem;
  border: 1px solid var(--color-border);
  flex-shrink: 0;
}

.stat {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-accent);
  line-height: 1;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--color-text-dim);
  margin-top: 0.3rem;
}

.hero-wave {
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 40px;
  background: repeating-linear-gradient(45deg, var(--color-accent) 0px, var(--color-accent) 2px, transparent 2px, transparent 8px);
  opacity: 0.2;
}

/* 响应式 */
@media (max-width: 768px) {
  .hero {
    padding: 3rem 0 4rem;
  }
  .hero-title {
    font-size: 2rem;
  }
  .hero-content {
    flex-direction: column;
    text-align: center;
  }
  .hero-stats {
    width: 100%;
    justify-content: center;
  }
}
</style>
