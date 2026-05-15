<!-- 导航栏 -->
<template>
  <header class="navbar-header">
    <div class="container-wide">
      <nav class="navbar">
        <div class="logo">
          <router-link to="/">
            <i class="fas fa-wave-square"></i>
            <span>DIZZYL@B</span>
          </router-link>
        </div>

        <div class="nav-links">
          <router-link to="/" exact-active-class="active">首页</router-link>
          <router-link to="/tag">标签</router-link>
          <router-link to="/labels">社团</router-link>
        </div>

        <div class="search-container">
          <input
            type="text"
            placeholder="搜索专辑、社团..."
            class="search-input"
            v-model="searchQuery"
            @keyup.enter="onSearch"
          >
        </div>

        <div class="auth-buttons">
          <button class="btn btn-login" @click="$emit('login')">登录</button>
          <button class="btn btn-register" @click="$emit('register')">注册</button>
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
    return {
      searchQuery: ''
    };
  },
  methods: {
    onSearch() {
      this.$emit('search', this.searchQuery);
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

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--color-accent);
}

.logo a {
  color: inherit;
  text-decoration: none;
}

.logo i {
  margin-right: 10px;
}

.nav-links {
  display: flex;
  gap: var(--spacing-xl);
}

.nav-links a {
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: color var(--transition-normal);
  font-size: 1rem;
  position: relative;
  padding: var(--spacing-sm) 0;
}

.nav-links a.router-link-exact-active,
.nav-links a:hover {
  color: var(--color-accent);
}

.nav-links a::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background-color: var(--color-accent);
  transition: width var(--transition-normal);
}

.nav-links a:hover::after,
.nav-links a.router-link-exact-active::after {
  width: 100%;
}

.search-container {
  display: flex;
  align-items: center;
  background: var(--color-border);
  padding: 0.2rem;
  flex: 1;
  max-width: 300px;
  margin: 0 var(--spacing-xl);
}

.search-input {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
}

.auth-buttons {
  display: flex;
  gap: 0;
}

.btn {
  padding: var(--spacing-sm) 1.2rem;
  cursor: pointer;
  font-weight: 500;
  transition: all var(--transition-normal);
  border: none;
  font-size: 0.9rem;
  color: var(--color-text-primary);
}

.btn-login {
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border-light);
}

.btn-register {
  background: #4CAF50;
}
</style>
