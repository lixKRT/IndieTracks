<template>
  <div class="user-profile container-wide">
    <LoadingSpinner v-if="loading" />

    <template v-else-if="user">
      <!-- 用户头部 -->
      <div class="profile-header">
        <div class="profile-avatar" @click="isOwner && $refs.avatarInput.click()">
          <img v-if="user.avatar_url" :src="user.avatar_url" :alt="user.username" />
          <div v-else class="avatar-placeholder"><i class="fas fa-user"></i></div>
          <div v-if="isOwner" class="avatar-overlay"><i class="fas fa-camera"></i></div>
        </div>
        <input ref="avatarInput" type="file" accept="image/*" style="display:none" @change="handleAvatarUpload" />
        <div class="profile-info">
          <h1 class="profile-name">{{ user.username }}</h1>
          <p class="profile-role">{{ user.user_role === 'pro' ? '社团成员' : '普通用户' }}</p>
          <button
            v-if="userStore.isLoggedIn && !isOwner"
            class="follow-btn"
            :class="{ followed: isFollowed }"
            @click="handleToggleFollow"
          >{{ isFollowed ? '已关注' : '关注' }}</button>
        </div>
      </div>

      <!-- Tab 切换 -->
      <div class="tabs">
        <button class="tab-btn" :class="{ active: activeTab === 'favorites' }" @click="activeTab = 'favorites'">
          收藏 ({{ favorites.length }})
        </button>
        <button class="tab-btn" :class="{ active: activeTab === 'following' }" @click="activeTab = 'following'">
          关注 ({{ followingCircles.length + followingUsers.length }})
        </button>
      </div>

      <!-- 收藏专辑 -->
      <div v-if="activeTab === 'favorites'" class="tab-content">
        <EmptyState v-if="favorites.length === 0" message="暂无收藏" />
        <AlbumGrid
          v-else
          :albums="favorites"
          :loading="false"
          :favorited-ids="favorite.favoriteAlbumIds"
          @album-click="goToAlbum"
          @circle-click="goToCircle"
          @tag-click="goToTag"
          @toggle-favorite="handleToggleFavorite"
        />
      </div>

      <!-- 关注 -->
      <div v-if="activeTab === 'following'" class="tab-content">
        <!-- 子分类 -->
        <div class="sub-tabs">
          <button class="sub-tab-btn" :class="{ active: followTab === 'circles' }" @click="followTab = 'circles'">
            社团 ({{ followingCircles.length }})
          </button>
          <button class="sub-tab-btn" :class="{ active: followTab === 'users' }" @click="followTab = 'users'">
            用户 ({{ followingUsers.length }})
          </button>
        </div>

        <!-- 关注社团 -->
        <div v-if="followTab === 'circles'">
          <EmptyState v-if="followingCircles.length === 0" message="暂未关注社团" />
          <div v-else class="circles-grid">
            <CircleCard
              v-for="c in followingCircles"
              :key="c.circle_id"
              :circle="c"
              :is-followed="c._followed !== false"
              @circle-click="goToCircleById(c.circle_id)"
              @album-click="goToAlbum"
              @toggle-follow="handleToggleCircleFollow"
            />
          </div>
        </div>

        <!-- 关注用户 -->
        <div v-if="followTab === 'users'">
          <EmptyState v-if="followingUsers.length === 0" message="暂未关注用户" />
          <div v-else class="follow-grid">
            <div v-for="u in followingUsers" :key="u.user_id" class="follow-card user-card">
              <div class="follow-card-avatar" @click="goToUser(u)">
                <img v-if="u.avatar_url" :src="u.avatar_url" :alt="u.username" />
                <div v-else class="avatar-placeholder"><i class="fas fa-user"></i></div>
              </div>
              <h3 class="follow-card-name" @click="goToUser(u)">{{ u.username }}</h3>
              <span class="follow-card-count" v-if="u.circle_name">{{ u.circle_name }}</span>
              <span class="follow-card-count" v-else-if="u.user_role === 'pro'">STAFF</span>
              <button
                v-if="u._followed !== false"
                class="card-follow-btn followed"
                @click.stop="handleUnfollowUser(u)"
                title="取消关注"
              >已关注</button>
              <button
                v-else
                class="card-follow-btn"
                @click.stop="handleRefollowUser(u)"
              >关注</button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useUserStore } from '../stores/user.js';
import { useFavoriteStore } from '../stores/favorite.js';
import { useNavigation } from '../composables/navigation.js';
import { useAuthGuard } from '../composables/authGuard.js';
import AlbumGrid from '../components/organisms/AlbumGrid.vue';
import CircleCard from '../components/molecules/CircleCard.vue';
import LoadingSpinner from '../components/atoms/LoadingSpinner.vue';
import EmptyState from '../components/atoms/EmptyState.vue';
import { fetchUser, getUserFavorites, getUserFollowingCircles, getUserFollowingUsers, checkUserFollow, followUser as apiFollowUser, unfollowUser as apiUnfollowUser, unfollowCircle as apiUnfollowCircle, followCircle as apiFollowCircle, uploadAvatar } from '../api';

export default {
  name: 'UserProfile',
  components: { AlbumGrid, CircleCard, LoadingSpinner, EmptyState },
  setup() {
    const route = useRoute();
    const userStore = useUserStore();
    const favorite = useFavoriteStore();
    const { goToAlbum, goToCircle, goToTag, goToUser, goToCircleById } = useNavigation();
    const { guard } = useAuthGuard();
    const user = ref(null);
    const loading = ref(true);
    const activeTab = ref('favorites');
    const followTab = ref('circles');
    const favorites = ref([]);
    const followingCircles = ref([]);
    const followingUsers = ref([]);
    const isFollowed = ref(false);

    const isOwner = computed(() => {
      return userStore.isLoggedIn && userStore.user?.user_id === parseInt(route.params.id);
    });

    async function loadData() {
      loading.value = true;
      const id = route.params.id;
      try {
        user.value = await fetchUser(id);

        const [favRes, circRes, userRes] = await Promise.allSettled([
          getUserFavorites(id),
          getUserFollowingCircles(id),
          getUserFollowingUsers(id)
        ]);
        favorites.value = favRes.status === 'fulfilled' ? favRes.value : [];
        followingCircles.value = circRes.status === 'fulfilled' ? circRes.value : [];
        followingUsers.value = userRes.status === 'fulfilled' ? userRes.value : [];

        // 加载当前用户的收藏状态到 store（用于按钮高亮）
        if (userStore.isLoggedIn) {
          await favorite.loadAll();
        }

        if (userStore.isLoggedIn && userStore.user?.user_id !== parseInt(id)) {
          try {
            const s = await checkUserFollow(id);
            isFollowed.value = s.followed;
          } catch { /* ignore */ }
        }
      } catch (e) {
        console.error('加载用户信息失败:', e);
      } finally {
        loading.value = false;
      }
    }

    async function handleToggleFavorite(album) {
      await guard(
        () => favorite.toggleFavorite(album.album_id),
        () => alert('请先登录')
      );
    }

    async function handleToggleFollow() {
      await guard(async () => {
        const id = route.params.id;
        if (isFollowed.value) {
          await apiUnfollowUser(id);
          isFollowed.value = false;
        } else {
          await apiFollowUser(id);
          isFollowed.value = true;
        }
      }, () => alert('请先登录'));
    }

    async function handleAvatarUpload(e) {
      const file = e.target.files[0];
      if (!file) return;
      try {
        const data = await uploadAvatar(file);
        user.value.avatar_url = data.avatar_url;
        userStore.user.avatar_url = data.avatar_url;
      } catch (err) {
        alert('上传失败: ' + (err.response?.data?.error || err.message));
      }
    }

    // 修复：函数名不再与 API 导入冲突
    async function handleUnfollowUser(u) {
      await apiUnfollowUser(u.user_id);
      u._followed = false;
    }

    async function handleRefollowUser(u) {
      await apiFollowUser(u.user_id);
      u._followed = true;
    }

    async function handleUnfollowCircle(c) {
      await apiUnfollowCircle(c.circle_id);
      c._followed = false;
    }

    async function handleRefollowCircle(c) {
      await apiFollowCircle(c.circle_id);
      c._followed = true;
    }

    async function handleToggleCircleFollow(circle) {
      await guard(async () => {
        if (circle._followed !== false) {
          await apiUnfollowCircle(circle.circle_id);
          circle._followed = false;
        } else {
          await apiFollowCircle(circle.circle_id);
          circle._followed = true;
        }
      }, () => alert('请先登录'));
    }

    onMounted(loadData);
    watch(() => route.params.id, loadData);

    return {
      user, loading, activeTab, followTab, favorites, followingCircles, followingUsers,
      isFollowed, isOwner, handleToggleFollow, handleToggleFavorite, handleAvatarUpload,
      handleUnfollowUser, handleRefollowUser, handleUnfollowCircle, handleRefollowCircle, handleToggleCircleFollow,
      userStore, favorite, goToAlbum, goToCircle, goToTag, goToUser, goToCircleById
    };
  }
};
</script>

<style scoped>
.profile-header { display: flex; align-items: center; gap: 2rem; padding: 3rem 0 2rem; }
.profile-avatar { width: 96px; height: 96px; flex-shrink: 0; position: relative; cursor: default; }
.profile-avatar img { width: 100%; height: 100%; object-fit: cover; }
.avatar-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; color: var(--color-text-primary); font-size: 1.2rem; opacity: 0; transition: opacity 0.2s; cursor: pointer; }
.profile-avatar:hover .avatar-overlay { opacity: 1; }
.avatar-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: var(--color-bg-secondary); color: var(--color-text-dim); font-size: 2.5rem; }
.profile-name { font-size: 1.8rem; font-weight: 700; color: var(--color-text-primary); margin-bottom: 0.3rem; }
.profile-role { font-size: 0.85rem; color: var(--color-text-muted); margin-bottom: 0.8rem; }

.follow-btn { padding: 0.4rem 1.5rem; background: var(--color-accent); color: var(--color-text-primary); border: none; font-size: 0.85rem; cursor: pointer; transition: all 0.2s; }
.follow-btn.followed { background: transparent; border: 1px solid var(--color-border); color: var(--color-text-muted); }

.tabs { display: flex; gap: 0; border-bottom: 1px solid var(--color-border); margin-bottom: 1.5rem; }
.tab-btn { padding: 0.8rem 1.5rem; background: none; border: none; color: var(--color-text-muted); font-size: 0.9rem; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.2s; }
.tab-btn.active { color: var(--color-accent); border-bottom-color: var(--color-accent); }
.tab-btn:hover { color: var(--color-text-primary); }

.sub-tabs { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
.sub-tab-btn { padding: 0.4rem 1rem; background: none; border: 1px solid var(--color-border); color: var(--color-text-muted); font-size: 0.8rem; cursor: pointer; transition: all 0.2s; }
.sub-tab-btn.active { background: var(--color-accent); border-color: var(--color-accent); color: var(--color-text-primary); }
.sub-tab-btn:hover { border-color: var(--color-accent); color: var(--color-text-primary); }

.follow-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; }
.circles-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--spacing-xl); }
@media (max-width: 768px) { .circles-grid { grid-template-columns: 1fr; } }
.follow-card { background: var(--color-bg-secondary); border: 1px solid var(--color-border); padding: 1.2rem; text-align: center; cursor: pointer; transition: all 0.2s; }
.follow-card:hover { border-color: var(--color-accent); transform: translateY(-2px); }
.follow-card-avatar { width: 64px; height: 64px; margin: 0 auto 0.8rem; }
.follow-card-avatar img { width: 100%; height: 100%; object-fit: cover; }
.follow-card-name { font-size: 0.9rem; color: var(--color-text-primary); margin-bottom: 0.3rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.follow-card-count { font-size: 0.75rem; color: var(--color-text-muted); margin-bottom: 0.5rem; display: block; }
.card-follow-btn { padding: 0.25rem 0.8rem; font-size: 0.7rem; cursor: pointer; transition: all 0.2s; border: none; margin-top: auto; background: var(--color-accent); color: var(--color-text-primary); }
.card-follow-btn.followed { background: transparent; border: 1px solid var(--color-border); color: var(--color-text-muted); }
.card-follow-btn.followed:hover { border-color: var(--color-accent); color: var(--color-accent); background: transparent; }
.user-card { display: flex; flex-direction: column; align-items: center; }

@media (max-width: 768px) {
  .profile-header { flex-direction: column; text-align: center; }
  .profile-avatar { width: 80px; height: 80px; }
}
</style>
