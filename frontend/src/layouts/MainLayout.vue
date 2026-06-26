<template>
  <div id="app-layout">
    <Navbar
      @search="handleSearch"
      @login="showLoginModal = true"
      @register="showRegisterModal = true"
    />

    <main class="layout-main">
      <router-view />
    </main>

    <PlayerBar />

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
            <input id="username" type="text" v-model="formData.username" required>
          </div>

          <!-- 登录时此字段同时接受用户名或邮箱 -->
          <div class="form-group">
            <label for="email">{{ showLoginModal ? '用户名或邮箱' : '邮箱' }}</label>
            <input id="email" :type="showLoginModal ? 'text' : 'email'" v-model="formData.email" required>
          </div>

          <div class="form-group">
            <label for="password">密码</label>
            <input id="password" type="password" v-model="formData.password" required>
          </div>

          <div v-if="showRegisterModal" class="form-group">
            <label for="confirmPassword">确认密码</label>
            <input id="confirmPassword" type="password" v-model="formData.confirmPassword" required>
          </div>

          <div v-if="showLoginModal" class="form-group remember-me">
            <label>
              <input type="checkbox" v-model="formData.rememberMe">
              <span>记住我（30天）</span>
            </label>
          </div>

          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

          <button type="submit" class="btn-submit" :disabled="submitting">
            {{ submitting ? '处理中...' : (showLoginModal ? '登录' : '注册') }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from '../components/organisms/Navbar.vue';
import FooterSection from '../components/organisms/FooterSection.vue';
import PlayerBar from '../components/organisms/PlayerBar.vue';
import { useUserStore } from '../stores/user.js';

// MainLayout — 全局布局壳：顶栏 + 主内容 + 底部播放栏 + 页脚 + 登录/注册弹窗
export default {
  name: 'MainLayout',
  components: { Navbar, FooterSection, PlayerBar },
  data() {
    return {
      showLoginModal: false,
      showRegisterModal: false,
      submitting: false,
      errorMsg: '',
      formData: { username: '', email: '', password: '', confirmPassword: '', rememberMe: false }
    };
  },
  setup() {
    const userStore = useUserStore();
    return { userStore };
  },
  mounted() {
    // 从 cookie/token 恢复登录状态，刷新页面后自动保持登录
    this.userStore.init();
  },
  methods: {
    handleSearch(query) {
      if (query.trim()) {
        this.$router.push({ path: '/tag', query: { search: query } });
      }
    },
    closeModals() {
      this.showLoginModal = false;
      this.showRegisterModal = false;
      this.errorMsg = '';
      this.resetForm();
    },
    resetForm() {
      this.formData = { username: '', email: '', password: '', confirmPassword: '', rememberMe: false };
    },
    async handleSubmit() {
      this.errorMsg = '';
      this.submitting = true;
      try {
        if (this.showRegisterModal) {
          if (this.formData.password !== this.formData.confirmPassword) {
            this.errorMsg = '密码不匹配';
            return;
          }
          await this.userStore.doRegister({
            username: this.formData.username,
            email: this.formData.email,
            password: this.formData.password
          });
        } else {
          // 后端 account 字段接受用户名或邮箱；remember_me 为 snake_case，与后端一致
          await this.userStore.doLogin({
            account: this.formData.email,
            password: this.formData.password,
            remember_me: this.formData.rememberMe
          });
        }
        this.closeModals();
      } catch (e) {
        // Axios 错误结构：e.response.data.error 由后端统一返回
        this.errorMsg = e.response?.data?.error || '操作失败';
      } finally {
        this.submitting = false;
      }
    }
  }
};
</script>

<style scoped>
.layout-main {
  min-height: 100vh;
  padding-bottom: 80px; /* 底部播放栏(PlayerBar)固定 80px，防止内容被遮挡 */
  overflow-anchor: none; /* 禁用浏览器自动滚动锚定，避免动态内容导致页面跳动 */
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  padding: 2rem;
  width: 400px;
  max-width: 90vw;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h3 {
  font-size: 1.2rem;
  color: var(--color-text-primary);
}

.modal-close {
  background: none;
  border: none;
  color: var(--color-text-dim);
  font-size: 1.5rem;
  cursor: pointer;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin-bottom: 0.3rem;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="password"] {
  width: 100%;
  padding: 0.6rem;
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  font-size: 0.9rem;
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.remember-me label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  cursor: pointer;
}

.remember-me input[type="checkbox"] {
  accent-color: var(--color-accent);
}

.error-msg {
  color: var(--color-accent);
  font-size: 0.85rem;
  margin: 0;
}

.btn-submit {
  padding: 0.7rem;
  background: var(--color-accent);
  color: var(--color-text-primary);
  border: none;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-submit:hover:not(:disabled) {
  background: var(--color-accent-hover);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: default;
}
</style>
