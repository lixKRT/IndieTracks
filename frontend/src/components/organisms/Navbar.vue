<!-- 导航栏 -->
<template>
  <header class="navbar-header">
    <div class="container-wide">
      <nav class="navbar">
        <div class="logo">
          <router-link to="/"><i class="fas fa-wave-square"></i><span>DIZZYL@B</span></router-link>
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
          <div class="auth-buttons">
            <button class="btn btn-login" @click="$emit('login')">登录</button>
            <button class="btn btn-register" @click="$emit('register')">注册</button>
          </div>
        </div>
      </nav>
    </div>
  </header>
</template>

<script>
export default {
  name: 'Navbar',
  emits: ['search', 'login', 'register'],
  data() {
    return { searchQuery: '', mobileOpen: false };
  },
  methods: {
    onSearch() {
      if (this.searchQuery.trim()) {
        this.$emit('search', this.searchQuery);
        this.mobileOpen = false;
      }
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

@media (max-width: 768px) {
  .hamburger { display: flex; }
  .nav-menu { display: none; width: 100%; flex-direction: column; align-items: stretch; gap: var(--spacing-md); padding-top: var(--spacing-md); }
  .nav-menu.open { display: flex; }
  .nav-links { flex-direction: column; gap: var(--spacing-sm); }
  .nav-links a { font-size: 1.1rem; }
  .search-container { max-width: none; width: 100%; }
  .auth-buttons { flex-direction: column; }
  .btn { text-align: center; padding: var(--spacing-sm); }
}
</style>
