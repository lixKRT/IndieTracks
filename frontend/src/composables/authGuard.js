import { useUserStore } from '../stores/user.js'

/**
 * 登录守卫 composable — 统一 "请先登录" 逻辑
 *
 * - 检查是否登录，未登录时调用 onNotLoggedIn 回调
 * - 执行 action，如果后端返回 401/403 则自动登出并提示
 */
export function useAuthGuard() {
  const userStore = useUserStore()

  /**
   * @param {Function} action - 已登录时执行的动作（可以返回 Promise）
   * @param {Function} [onNotLoggedIn] - 未登录时的回调（如 alert 或打开登录弹窗）
   * @returns {Promise<boolean>} 是否成功执行
   */
  async function guard(action, onNotLoggedIn) {
    if (!userStore.isLoggedIn) {
      if (onNotLoggedIn) onNotLoggedIn()
      return false
    }
    try {
      await action()
      return true
    } catch (e) {
      // 后端返回 401/403 → cookie 过期或无效，自动登出
      if (e.response?.status === 401 || e.response?.status === 403) {
        userStore.user = null
        if (onNotLoggedIn) onNotLoggedIn()
      } else {
        console.error('操作失败:', e)
      }
      return false
    }
  }

  // isLoggedIn 为创建时的布尔快照，非响应式引用
  return { guard, isLoggedIn: userStore.isLoggedIn }
}
