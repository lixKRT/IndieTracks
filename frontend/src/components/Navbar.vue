<!-- 导航栏 -->
<template>
  <header>
    <div class="container-full">
      <nav class="navbar">
        <div class="logo">
          <router-link to="/">
            <i class="fas fa-wave-square"></i>
            <span>DIZZYL@B</span>
          </router-link>
        </div>

        <div class="nav-links">
          <router-link to="/" exact-active-class="active">首页</router-link>
          <router-link to="/labels">社团</router-link>
        </div>

        <div class="search-container">
          <input
            type="text"
            placeholder="搜索专辑、艺术家..."
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
/* Header */
header {
  background-color: rgba(10, 10, 10, 0.95);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #222;
  padding: 1rem 0;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.8rem;
  font-weight: 700;
  color: #ff6b6b;
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
  gap: 2rem;
}

.nav-links a {
  color: #ddd;
  text-decoration: none;
  transition: color 0.3s;
  font-size: 1rem;
  position: relative;
  padding: 0.5rem 0;
}

.nav-links a.router-link-exact-active,
.nav-links a:hover {
  color: #ff6b6b;
}

.nav-links a::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background-color: #ff6b6b;
  transition: width 0.3s;
}

.nav-links a:hover::after,
.nav-links a.router-link-exact-active::after {
  width: 100%;
}

.search-container {
  display: flex;
  align-items: center;
  background: #222;
  border-radius: 0;
  padding: 0.2rem;
  flex: 1;
  max-width: 300px;
  margin: 0 2rem;
}

.search-input {
  flex: 1;
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
  color: white;
  font-size: 1rem;
  border-radius: 0;
}

.search-input:focus {
  outline: none;
}

.auth-buttons {
  display: flex;
  gap: 0;
}

.btn {
  padding: 0.5rem 1.2rem;
  border-radius: 0;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
  border: none;
  text-decoration: none;
  font-size: 0.9rem;
  color: white;
  border-bottom: 1px solid #333;
}

.btn:first-child {
  border-left: 1px solid #333;
}

.btn:last-child {
  border-right: 1px solid #333;
}

.btn-login {
  background: #1a1a1a;
  border-right: 1px solid #333;
}

.btn-register {
  background: #4CAF50;
  border: none;
}
</style>
