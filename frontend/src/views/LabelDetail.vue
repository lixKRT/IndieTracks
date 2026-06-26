<template>
  <div class="label-detail container-wide">
    <LoadingSpinner v-if="loading" />

    <template v-else-if="circle">
      <!-- 社团头部 Hero -->
      <div class="detail-hero">
        <div class="detail-header">
          <div class="detail-logo-wrapper">
            <img :src="circle.logo_url" :alt="circle.name" class="detail-logo">
          </div>
          <div class="detail-info">
            <h1 class="detail-name">{{ circle.name }}</h1>
            <p class="detail-desc">{{ circle.description }}</p>
            <div class="detail-stats">
              <span><i class="fas fa-compact-disc"></i> {{ circle.albums.length }} 张专辑</span>
              <span><i class="fas fa-user-friends"></i> {{ circle.members.length }} 名成员</span>
              <button
                class="follow-btn"
                :class="{ followed: isFollowed }"
                @click="toggleFollow"
              >{{ isFollowed ? '已关注' : '关注社团' }}</button>
            </div>
            <div class="circle-tags" v-if="circle.representative_tags && circle.representative_tags.length">
              <span
                v-for="tag in circle.representative_tags"
                :key="tag"
                class="tag"
                @click.stop="goToTag(tag)"
              >#{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 成员列表 -->
      <section v-if="circle.members.length > 0" class="detail-section">
        <h2 class="section-title">
          <i class="fas fa-users"></i> 成员
        </h2>
        <div class="member-list">
          <div v-for="m in circle.members" :key="m.user_id" class="member-item" @click="goToUser(m)">
            <img :src="m.avatar_url" :alt="m.username" class="member-avatar">
            <div class="member-info">
              <span class="member-name">{{ m.username }}</span>
              <span class="member-role">{{ m.user_role === 'pro' ? '创作者' : '听众' }}</span>
            </div>
          </div>
        </div>
      </section>

      <section v-if="circle.albums.length > 0" class="detail-section">
        <h2 class="section-title">
          <i class="fas fa-music"></i> 专辑作品
        </h2>
        <div class="albums-grid">
          <AlbumCard
            v-for="album in enhancedAlbums"
            :key="album.album_id"
            :album="album"
            :is-favorited="favorite.isFavorite(album.album_id)"
            @album-click="goToAlbum"
            @circle-click="goToCircle"
            @tag-click="goToTag"
            @preview="handlePreview"
            @toggle-favorite="handleToggleFavorite"
          />
        </div>
      </section>
    </template>
  </div>
</template>

<script>
import { fetchCircle, checkCircleFollow, followCircle, unfollowCircle } from '../api';
import { useFavoriteStore } from '../stores/favorite.js';
import { useUserStore } from '../stores/user.js';
import { useNavigation } from '../composables/navigation.js';
import { useAuthGuard } from '../composables/authGuard.js';
import { usePreviewPlay } from '../composables/previewPlay.js';
import AlbumCard from '../components/molecules/AlbumCard.vue';
import LoadingSpinner from '../components/atoms/LoadingSpinner.vue';

export default {
  name: 'LabelDetailView',
  components: { AlbumCard, LoadingSpinner },
  data() {
    return { circle: null, loading: true, isFollowed: false };
  },
  setup() {
    const userStore = useUserStore();
    const favorite = useFavoriteStore();
    const { goToAlbum, goToCircle, goToTag, goToUser } = useNavigation();
    const { guard } = useAuthGuard(); // 未登录操作时弹窗提示
    const { addPreview } = usePreviewPlay();
    return { userStore, favorite, goToAlbum, goToCircle, goToTag, goToUser, guard, addPreview };
  },
  computed: {
    // 专辑 API 不返回所属社团 logo，这里从 circle 对象注入
    enhancedAlbums() {
      if (!this.circle) return [];
      return this.circle.albums.map(album => ({
        ...album,
        circle_logo_url: this.circle.logo_url
      }));
    }
  },
  async mounted() {
    try {
      const id = this.$route.params.id;
      this.circle = await fetchCircle(id);
      if (this.userStore.isLoggedIn) {
        try {
          const data = await checkCircleFollow(id);
          this.isFollowed = data.followed;
        } catch { /* ignore */ }
      }
    } catch (e) {
      console.error('加载社团详情失败:', e);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    async toggleFollow() {
      await this.guard(async () => {
        const id = this.$route.params.id;
        if (this.isFollowed) {
          await unfollowCircle(id);
          this.isFollowed = false;
        } else {
          await followCircle(id);
          this.isFollowed = true;
        }
      }, () => alert('请先登录'));
    },
    async handlePreview(album) {
      await this.addPreview(album.album_id);
    },
    handleToggleFavorite(album) {
      this.guard(
        () => this.favorite.toggleFavorite(album.album_id),
        () => alert('请先登录')
      );
    }
  }
};
</script>

<style scoped>
.label-detail {
  padding-top: var(--spacing-xl);
  padding-bottom: var(--spacing-2xl);
}

.detail-hero {
  /* 暗色渐变 Hero 区域，与页面主背景形成层次 */
  background: linear-gradient(135deg, rgba(20,20,20,0.9) 0%, rgba(10,10,10,0.95) 100%);
  border: 1px solid var(--color-border);
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-xl);
}

.detail-header {
  display: flex;
  gap: var(--spacing-xl);
  align-items: center;
  flex-wrap: wrap;
}

.detail-logo-wrapper {
  flex-shrink: 0;
  width: 140px;
  height: 140px;
  overflow: hidden;
  transition: transform 0.3s;
}

.detail-logo-wrapper:hover {
  transform: scale(1.02);
  border-color: var(--color-accent);
}

.detail-logo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-info {
  flex: 1;
  min-width: 200px;
}

.detail-name {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
  letter-spacing: -0.3px;
}

.detail-desc {
  font-size: 0.95rem;
  color: var(--color-text-muted);
  line-height: 1.6;
  margin-bottom: var(--spacing-md);
}

.detail-stats {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  font-size: 0.85rem;
  color: var(--color-text-dim);
}

.follow-btn {
  padding: 0.4rem 1.2rem;
  background: var(--color-accent);
  color: var(--color-text-primary);
  border: none;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.follow-btn.followed {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
}

.detail-stats i {
  margin-right: 6px;
  width: 16px;
  color: var(--color-accent);
}

.circle-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 12px;
}

.tag {
  background: linear-gradient(135deg, rgba(255,107,107,0.12), rgba(255,107,107,0.05));
  color: var(--color-accent);
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tag:hover {
  background: rgba(255, 107, 107, 0.2);
}

.detail-section {
  margin-top: var(--spacing-xl);
}

.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
  border-left: 4px solid var(--color-accent);
  padding-left: var(--spacing-md);
}

.section-title i {
  margin-right: 8px;
  color: var(--color-accent);
}

.member-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.member-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  background: var(--color-bg-secondary);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  transition: background 0.2s, border-color 0.2s;
  cursor: pointer;
}

.member-item:hover {
  background: var(--color-bg-tertiary);
  border-color: var(--color-accent);
}

.member-avatar {
  width: 48px;
  height: 48px;
  object-fit: cover;
  flex-shrink: 0;
}

.member-info {
  flex: 1;
}

.member-name {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.member-role {
  font-size: 0.7rem;
  color: var(--color-text-dim);
}


.albums-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-xl);
}


@media (max-width: 768px) {
  .albums-grid {
    grid-template-columns: 1fr;
  }
  .detail-header {
    flex-direction: column;
    text-align: center;
  }
  .detail-logo-wrapper {
    width: 100px;
    height: 100px;
  }
  .detail-stats {
    justify-content: center;
  }
}
</style>
