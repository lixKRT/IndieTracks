<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <router-link to="/" class="back-link">
          <i class="fas fa-arrow-left"></i>
          <span>返回前台</span>
        </router-link>
        <h2 class="sidebar-title">管理后台</h2>
      </div>

      <nav class="sidebar-nav">
        <!-- exact-active-class: 仅完全匹配 /admin 时激活，避免子路由也高亮 -->
        <router-link to="/admin" class="nav-item" exact-active-class="active">
          <i class="fas fa-chart-line"></i>
          <span>数据透视</span>
        </router-link>
        <router-link to="/admin/albums" class="nav-item" active-class="active">
          <i class="fas fa-compact-disc"></i>
          <span>专辑管理</span>
        </router-link>
        <router-link v-if="isStaff" to="/admin/circles" class="nav-item" active-class="active">
          <i class="fas fa-users"></i>
          <span>社团管理</span>
        </router-link>
        <router-link v-if="isStaff" to="/admin/users" class="nav-item" active-class="active">
          <i class="fas fa-user"></i>
          <span>用户管理</span>
        </router-link>
        <router-link v-if="isStaff" to="/admin/tags" class="nav-item" active-class="active">
          <i class="fas fa-tag"></i>
          <span>标签管理</span>
        </router-link>
        <router-link to="/admin/comments" class="nav-item" active-class="active">
          <i class="fas fa-comment"></i>
          <span>评论管理</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <img v-if="userStore.user?.avatar_url" :src="userStore.user.avatar_url" class="user-avatar" />
          <span v-else class="user-avatar-placeholder"><i class="fas fa-user"></i></span>
          <div class="user-details">
            <span class="user-name">{{ userStore.user?.username }}</span>
            <span class="user-role">{{ userStore.user?.user_role === 'staff' ? '管理员' : '社团成员' }}</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- 内容区 -->
    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>

<script>
import { useUserStore } from '../stores/user.js';

// AdminLayout — 管理后台布局壳：侧边导航 + 内容区
export default {
  name: 'AdminLayout',
  setup() {
    const userStore = useUserStore();
    return { userStore };
  },
  computed: {
    // staff 角色才能看到社团/用户/标签管理入口
    isStaff() {
      return this.userStore.user?.user_role === 'staff';
    }
  }
};
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg-primary);
}

/* 侧边栏 */
.admin-sidebar {
  width: 240px;
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.back-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.85rem;
  margin-bottom: var(--spacing-md);
  transition: color var(--transition-fast);
}

.back-link:hover {
  color: var(--color-accent);
}

.sidebar-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.sidebar-nav {
  flex: 1;
  padding: var(--spacing-md) 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.9rem;
  transition: all var(--transition-fast);
  border-left: 3px solid transparent;
}

.nav-item:hover {
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.03);
}

.nav-item.active {
  color: var(--color-accent);
  background: rgba(255, 107, 107, 0.06);
  border-left-color: var(--color-accent);
}

.nav-item i {
  width: 20px;
  text-align: center;
}

.sidebar-footer {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.user-avatar {
  width: 36px;
  height: 36px;
  object-fit: cover;
  border: 1px solid var(--color-border);
}

.user-avatar-placeholder {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-tertiary);
  color: var(--color-text-dim);
  font-size: 0.9rem;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 0.85rem;
  color: var(--color-text-primary);
}

.user-role {
  font-size: 0.75rem;
  color: var(--color-text-dim);
}

/* 内容区 */
.admin-main {
  flex: 1;
  padding: var(--spacing-xl);
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--color-border) transparent;
}

.admin-main::-webkit-scrollbar {
  width: 6px;
}

.admin-main::-webkit-scrollbar-track {
  background: transparent;
}

.admin-main::-webkit-scrollbar-thumb {
  background: var(--color-border);
}

.admin-main::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-dim);
}

/* 移动端：侧边栏收缩为仅图标模式 */
@media (max-width: 768px) {
  .admin-sidebar {
    width: 60px;
  }

  .sidebar-header,
  .sidebar-footer {
    display: none;
  }

  .nav-item span {
    display: none;
  }

  .nav-item {
    justify-content: center;
    padding: var(--spacing-md);
  }
}
</style>
