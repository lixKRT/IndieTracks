// 用户 Store — 登录态管理，基于 HttpOnly Cookie + JWT 认证
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { register, login, logout, fetchMe } from '../api';

export const useUserStore = defineStore('user', () => {
  const user = ref(null);
  const isLoggedIn = computed(() => !!user.value);

  async function doRegister(form) {
    const data = await register(form);
    user.value = data;
    return data;
  }

  async function doLogin(form) {
    const data = await login(form);
    user.value = data;
    return data;
  }

  // 登出：即使后端请求失败也清除本地状态
  async function doLogout() {
    try { await logout(); } catch { /* ignore */ }
    user.value = null;
  }

  // 初始化：通过 /me 接口用 HttpOnly Cookie 恢复登录态
  async function init() {
    try {
      const data = await fetchMe();
      user.value = data;
    } catch {
      // cookie 无效或过期，清除本地状态
      user.value = null;
    }
  }

  return { user, isLoggedIn, doRegister, doLogin, doLogout, init };
});
