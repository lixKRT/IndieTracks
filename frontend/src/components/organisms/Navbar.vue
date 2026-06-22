<!-- 导航栏 -->
<template>
  <header class="navbar-header">
    <div class="container-wide">
      <nav class="navbar">
        <div class="logo">
          <router-link to="/"><i class="fas fa-wave-square"></i><span>IndieTracks</span></router-link>
        </div>

        <button class="hamburger" @click="mobileOpen = !mobileOpen" aria-label="菜单">
          <span class="hbar"></span><span class="hbar"></span><span class="hbar"></span>
        </button>

        <div class="nav-menu" :class="{ open: mobileOpen }">
          <div class="nav-links">
            <router-link to="/" exact-active-class="active" @click="mobileOpen = false">首页</router-link>
            <router-link to="/tag" @click="mobileOpen = false">标签</router-link>
            <router-link to="/labels" @click="mobileOpen = false">社团</router-link>
          </div>
          <div class="search-container">
            <input type="text" placeholder="搜索专辑、社团..." class="search-input" v-model="searchQuery" @keyup.enter="onSearch">
          </div>

          <!-- 已登录 -->
          <div v-if="userStore.isLoggedIn" class="user-menu">
            <div class="user-actions">
              <router-link to="/cart" class="cart-icon" @click="mobileOpen = false">
                <i class="fas fa-shopping-cart"></i>
                <span v-if="cartCount > 0" class="cart-badge">{{ cartCount }}</span>
              </router-link>
              <div class="user-info" @click="showDropdown = !showDropdown">
                <img v-if="userStore.user?.avatar_url" :src="userStore.user.avatar_url" class="user-avatar" />
                <span v-else class="user-avatar-placeholder"><i class="fas fa-user"></i></span>
                <span class="user-name">{{ userStore.user?.username }}</span>
              </div>
            </div>
            <div v-if="showDropdown" class="dropdown">
              <router-link :to="`/user/${userStore.user?.user_id}`" class="dropdown-item" @click="showDropdown = false">个人主页</router-link>
              <router-link to="/cart" class="dropdown-item" @click="showDropdown = false">购物车</router-link>
              <router-link
                v-if="userStore.user?.user_role === 'pro' || userStore.user?.user_role === 'staff'"
                to="/admin"
                class="dropdown-item admin-link"
                @click="showDropdown = false"
              >管理后台</router-link>
              <button class="dropdown-item" @click="handleLogout">退出登录</button>
            </div>
          </div>

          <!-- 未登录 -->
          <div v-else class="auth-buttons">
            <button class="btn btn-login" @click="$emit('login')">登录</button>
            <button class="btn btn-register" @click="$emit('register')">注册</button>
          </div>
        </div>
      </nav>
    </div>
  </header>
</template>

<script>
import { useUserStore } from '../../stores/user.js';
import { getCartCount } from '../../api';

export default {
  name: 'Navbar',
  emits: ['search', 'login', 'register'],
  data() {
    return { searchQuery: '', mobileOpen: false, showDropdown: false, cartCount: 0 };
  },
  setup() {
    return { userStore: useUserStore() };
  },
  watch: {
    'userStore.isLoggedIn': {
      immediate: true,
      handler(loggedIn) {
        if (loggedIn) {
          this.loadCartCount();
        } else {
          this.cartCount = 0;
        }
      }
    }
  },
  mounted() {
    window.addEventListener('cart-updated', this.loadCartCount);
  },
  beforeUnmount() {
    window.removeEventListener('cart-updated', this.loadCartCount);
  },
  methods: {
    onSearch() {
      if (this.searchQuery.trim()) {
        this.$emit('search', this.searchQuery);
        this.mobileOpen = false;
      }
    },
    async handleLogout() {
      await this.userStore.doLogout();
      this.showDropdown = false;
      this.mobileOpen = false;
      this.cartCount = 0;
      this.$router.push('/');
    },
    async loadCartCount() {
      try {
        const res = await getCartCount();
        this.cartCount = res.count;
      } catch { /* ignore */ }
    }
  }
};
</script>

<style scoped>
.navbar-header {
  background-color: rgba(10, 10, 10, 0.95);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid var(--color-border);
  padding: var(--spacing-md) 0;
}

.navbar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }

.logo { display: flex; align-items: center; font-size: 1.8rem; font-weight: 700; color: var(--color-accent); flex-shrink: 0; }
.logo a { color: inherit; text-decoration: none; }
.logo i { margin-right: 10px; }

.hamburger { display: none; flex-direction: column; gap: 5px; background: none; border: none; padding: var(--spacing-xs); cursor: pointer; }
.hbar { display: block; width: 24px; height: 2px; background: var(--color-text-primary); transition: all var(--transition-fast); }

.nav-menu { display: flex; align-items: center; gap: var(--spacing-xl); }
.nav-links { display: flex; gap: var(--spacing-xl); }
.nav-links a { color: var(--color-text-secondary); text-decoration: none; transition: color var(--transition-normal); font-size: 1rem; position: relative; padding: var(--spacing-sm) 0; white-space: nowrap; }
.nav-links a.router-link-exact-active, .nav-links a:hover { color: var(--color-accent); }
.nav-links a::after { content: ''; position: absolute; bottom: 0; left: 0; width: 0; height: 2px; background-color: var(--color-accent); transition: width var(--transition-normal); }
.nav-links a:hover::after, .nav-links a.router-link-exact-active::after { width: 100%; }

.search-container { display: flex; align-items: center; background: var(--color-border); padding: 0.2rem; max-width: 300px; }
.search-input { flex: 1; padding: var(--spacing-sm) var(--spacing-md); background: transparent; border: none; color: var(--color-text-primary); font-size: 1rem; min-width: 140px; }
.search-input:focus { outline: none; }

.auth-buttons { display: flex; gap: 0; flex-shrink: 0; }
.btn { padding: var(--spacing-sm) 1.2rem; cursor: pointer; font-weight: 500; transition: all var(--transition-normal); border: none; font-size: 0.9rem; color: var(--color-text-primary); }
.btn-login { background: var(--color-bg-secondary); border-right: 1px solid var(--color-border-light); }
.btn-register { background: #4CAF50; }

/* 用户菜单 */
.user-menu { position: relative; }
.user-actions { display: flex; align-items: center; gap: 0.5rem; }
.user-info { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; padding: 0.3rem 0.6rem; transition: background 0.2s; }
.user-info:hover { background: rgba(255,255,255,0.05); }
.user-avatar { width: 40px; height: 40px; object-fit: cover }
.user-avatar-placeholder { width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; background: var(--color-bg-tertiary); color: var(--color-text-dim); font-size: 1rem }
.user-name { font-size: 0.85rem; color: var(--color-text-primary); white-space: nowrap; }

.cart-icon {
  position: relative;
  color: var(--color-text-secondary);
  font-size: 1.2rem;
  cursor: pointer;
  transition: color var(--transition-fast);
  text-decoration: none;
  padding: 0.3rem;
}

.cart-icon:hover { color: var(--color-accent); }

.cart-badge {
  position: absolute;
  top: -6px;
  right: -8px;
  background: var(--color-accent);
  color: var(--color-text-primary);
  font-size: 0.65rem;
  font-weight: 700;
  min-width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  padding: 0 4px;
}

.dropdown { position: absolute; top: 100%; right: 0; background: var(--color-bg-secondary); border: 1px solid var(--color-border); min-width: 120px; z-index: 10; }
.dropdown-item { display: block; width: 100%; padding: 0.5rem 1rem; background: none; border: none; color: var(--color-text-primary); font-size: 0.85rem; text-align: left; cursor: pointer; text-decoration: none; transition: background 0.2s; }
.dropdown-item:hover { background: rgba(255,255,255,0.05); color: var(--color-accent); }
.admin-link { border-top: 1px solid var(--color-border); color: var(--color-accent); }

@media (max-width: 768px) {
  .hamburger { display: flex; }
  .nav-menu { display: none; width: 100%; flex-direction: column; align-items: stretch; gap: var(--spacing-md); padding-top: var(--spacing-md); }
  .nav-menu.open { display: flex; }
  .nav-links { flex-direction: column; gap: var(--spacing-sm); }
  .nav-links a { font-size: 1.1rem; }
  .search-container { max-width: none; width: 100%; }
  .auth-buttons { flex-direction: column; }
  .btn { text-align: center; padding: var(--spacing-sm); }
  .user-menu { width: 100%; }
  .dropdown { position: static; width: 100%; }
}
</style>
