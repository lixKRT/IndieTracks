<template>
  <div id="app">
    <Navbar
      @search="performSearch"
      @login="showLoginModal = true"
      @register="showRegisterModal = true"
    />

    <!-- 路由视图 -->
    <router-view />

    <FooterSection />

    <!-- Auth Modals -->
    <div
      v-if="showLoginModal || showRegisterModal"
      class="modal-overlay"
      @click="closeModals"
    >
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ showLoginModal ? '用户登录' : '用户注册' }}</h3>
          <button class="modal-close" @click="closeModals">&times;</button>
        </div>

        <form @submit.prevent="handleSubmit" class="auth-form">
          <div v-if="showRegisterModal" class="form-group">
            <label for="username">用户名</label>
            <input
              id="username"
              type="text"
              v-model="formData.username"
              required
            >
          </div>

          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              id="email"
              type="email"
              v-model="formData.email"
              required
            >
          </div>

          <div class="form-group">
            <label for="password">密码</label>
            <input
              id="password"
              type="password"
              v-model="formData.password"
              required
            >
          </div>

          <div v-if="showRegisterModal" class="form-group">
            <label for="confirmPassword">确认密码</label>
            <input
              id="confirmPassword"
              type="password"
              v-model="formData.confirmPassword"
              required
            >
          </div>

          <button type="submit" class="btn-submit">
            {{ showLoginModal ? '登录' : '注册' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue';
import FooterSection from './components/FooterSection.vue';

export default {
  name: 'App',
  components: {
    Navbar,
    FooterSection
  },
  data() {
    return {
      showLoginModal: false,
      showRegisterModal: false,
      formData: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
    };
  },
  methods: {
    performSearch(query) {
      if (query.trim()) {
        alert(`搜索: ${query}`);
      }
    },
    closeModals() {
      this.showLoginModal = false;
      this.showRegisterModal = false;
      this.resetForm();
    },
    resetForm() {
      this.formData = {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      };
    },
    handleSubmit() {
      if (
        this.showRegisterModal &&
        this.formData.password !== this.formData.confirmPassword
      ) {
        alert('密码不匹配！');
        return;
      }
      console.log(
        `${this.showLoginModal ? '登录' : '注册'} 表单提交:`,
        this.formData
      );
      this.closeModals();
    }
  }
};
</script>

<style>
@import './assets/style.css';
</style>
