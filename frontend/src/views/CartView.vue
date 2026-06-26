<template>
  <div class="cart-page container-wide">
    <div class="page-header">
      <h1 class="page-title">购物车</h1>
    </div>

    <LoadingSpinner v-if="loading" />

    <template v-else-if="cartItems.length > 0">
      <div class="cart-layout">
        <!-- 左侧：商品列表 -->
        <div class="cart-items">
          <div class="cart-select-all">
            <label class="checkbox-label">
              <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" />
              <span>全选 ({{ selectedIds.length }}/{{ cartItems.length }})</span>
            </label>
          </div>

          <div
            v-for="item in cartItems"
            :key="item.album_id"
            class="cart-item"
          >
            <label class="checkbox-label item-checkbox">
              <input type="checkbox" v-model="selectedIds" :value="item.album_id" />
            </label>

            <div class="item-cover" @click="goToAlbum(item)">
              <img :src="item.cover_url" :alt="item.title" />
            </div>

            <div class="item-info">
              <h3 class="item-title" @click="goToAlbum(item)">{{ item.title }}</h3>
              <p class="item-circle">{{ item.circle_name || '未知社团' }}</p>
            </div>

            <div class="item-price">
              <span v-if="item.price > 0" class="price-paid">¥ {{ item.price }}</span>
              <span v-else class="price-free">免费</span>
            </div>

            <button class="item-remove" @click="handleRemove(item)" title="移除">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <!-- 右侧：结算面板 -->
        <div class="cart-summary">
          <div class="summary-card">
            <h3 class="summary-title">订单详情</h3>
            <div class="summary-row">
              <span>已选商品</span>
              <span>{{ selectedIds.length }} 件</span>
            </div>
            <div class="summary-row total">
              <span>合计</span>
              <span class="total-price">¥ {{ totalPrice.toFixed(2) }}</span>
            </div>
            <button
              class="checkout-btn"
              :disabled="selectedIds.length === 0 || checkingOut"
              @click="handleCheckout"
            >
              <span v-if="checkingOut" class="loading">
                <span class="spinner"></span>
                处理中...
              </span>
              <span v-else>结算</span>
            </button>
          </div>
        </div>
      </div>
    </template>

    <EmptyState v-else message="购物车是空的" />

    <!-- 结算确认弹窗：Teleport 到 body 避免父容器 overflow/transform 影响定位 -->
    <Teleport to="body">
      <div v-if="showCheckoutModal" class="modal-overlay" @click.self="showCheckoutModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>确认结算</h3>
            <button class="modal-close" @click="showCheckoutModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <div class="checkout-items">
              <div v-for="item in selectedItems" :key="item.album_id" class="checkout-item">
                <img :src="item.cover_url" :alt="item.title" class="checkout-cover" />
                <div class="checkout-info">
                  <p class="checkout-title">{{ item.title }}</p>
                  <p class="checkout-circle">{{ item.circle_name }}</p>
                </div>
                <span class="checkout-price">
                  {{ item.price > 0 ? `¥${item.price}` : '免费' }}
                </span>
              </div>
            </div>
            <div class="checkout-total">
              <span>合计</span>
              <span class="total-price">¥ {{ totalPrice.toFixed(2) }}</span>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showCheckoutModal = false" :disabled="checkingOut">取消</button>
            <button class="btn-confirm" @click="confirmCheckout" :disabled="checkingOut">
              <span v-if="checkingOut" class="loading">
                <span class="spinner"></span>
                处理中...
              </span>
              <span v-else>确认支付</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
// CartView — 购物车页：商品列表（可勾选） + 结算面板 + 确认弹窗
import { ref, computed, onMounted } from 'vue'
import { getCart, removeFromCart, checkoutCart, getCartCount } from '../api'
import { useNavigation } from '../composables/navigation.js'
import LoadingSpinner from '../components/atoms/LoadingSpinner.vue'
import EmptyState from '../components/atoms/EmptyState.vue'

const { goToAlbum } = useNavigation() // composable 封装的路由跳转方法

const loading = ref(true)
const cartItems = ref([])
const selectedIds = ref([])
const selectAll = ref(true)
const showCheckoutModal = ref(false)
const checkingOut = ref(false)

const selectedItems = computed(() =>
  cartItems.value.filter(item => selectedIds.value.includes(item.album_id))
)

const totalPrice = computed(() =>
  selectedItems.value.reduce((sum, item) => sum + (item.price || 0), 0)
)

// selectAll checkbox 与 selectedIds 数组双向同步
function toggleSelectAll() {
  if (selectAll.value) {
    selectedIds.value = cartItems.value.map(item => item.album_id)
  } else {
    selectedIds.value = []
  }
}

async function loadCart() {
  loading.value = true
  try {
    cartItems.value = await getCart()
    selectedIds.value = cartItems.value.map(item => item.album_id)
  } catch (e) {
    console.error('加载购物车失败:', e)
  } finally {
    loading.value = false
  }
}

async function handleRemove(item) {
  try {
    await removeFromCart(item.album_id)
    cartItems.value = cartItems.value.filter(i => i.album_id !== item.album_id)
    selectedIds.value = selectedIds.value.filter(id => id !== item.album_id)
    // 更新 Navbar 角标（跨组件通信）
    window.dispatchEvent(new CustomEvent('cart-updated'))
  } catch (e) {
    console.error('移除失败:', e)
  }
}

function handleCheckout() {
  if (selectedIds.value.length === 0) return
  showCheckoutModal.value = true
}

async function confirmCheckout() {
  checkingOut.value = true
  try {
    await checkoutCart(selectedIds.value)
    // 结算成功后从本地列表移除已购买项，无需重新请求
    cartItems.value = cartItems.value.filter(item => !selectedIds.value.includes(item.album_id))
    selectedIds.value = []
    showCheckoutModal.value = false
    // 更新 Navbar 角标
    window.dispatchEvent(new CustomEvent('cart-updated'))
    alert('购买成功！')
  } catch (e) {
    console.error('结算失败:', e)
    alert('结算失败，请重试')
  } finally {
    checkingOut.value = false
  }
}

onMounted(loadCart)
</script>

<style scoped>
.cart-page {
  padding-top: var(--spacing-xl);
  padding-bottom: var(--spacing-2xl);
}

.page-header {
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.cart-layout {
  display: flex;
  gap: var(--spacing-xl);
  align-items: flex-start;
}

.cart-items {
  flex: 1;
  min-width: 0;
}

.cart-select-all {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--spacing-md);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--color-accent);
}

.cart-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  margin-bottom: var(--spacing-sm);
}

.item-checkbox {
  flex-shrink: 0;
}

.item-cover {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  cursor: pointer;
  overflow: hidden;
}

.item-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-title:hover {
  color: var(--color-accent);
}

.item-circle {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.item-price {
  font-size: 1rem;
  font-weight: 600;
  flex-shrink: 0;
}

.price-paid {
  color: var(--color-accent);
}

.price-free {
  color: #4caf50;
}

.item-remove {
  background: none;
  border: none;
  color: var(--color-text-dim);
  font-size: 1rem;
  cursor: pointer;
  padding: var(--spacing-sm);
  transition: color var(--transition-fast);
}

.item-remove:hover {
  color: var(--color-accent);
}

.cart-summary {
  width: 300px;
  flex-shrink: 0;
  position: sticky;
  top: 100px; /* 粘性定位，滚动时结算面板始终可见 */
}

.summary-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  padding: var(--spacing-xl);
}

.summary-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.summary-row.total {
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.total-price {
  color: var(--color-accent);
  font-size: 1.2rem;
}

.checkout-btn {
  width: 100%;
  padding: var(--spacing-md);
  background: var(--color-accent);
  color: var(--color-text-primary);
  border: none;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: var(--spacing-lg);
  transition: background var(--transition-fast);
}

.checkout-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
}

.checkout-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: var(--color-text-dim);
  font-size: 1.2rem;
  cursor: pointer;
}

.modal-body {
  padding: var(--spacing-lg);
  overflow-y: auto;
  flex: 1;
}

.checkout-items {
  margin-bottom: var(--spacing-lg);
}

.checkout-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border);
}

.checkout-item:last-child {
  border-bottom: none;
}

.checkout-cover {
  width: 48px;
  height: 48px;
  object-fit: cover;
  flex-shrink: 0;
}

.checkout-info {
  flex: 1;
  min-width: 0;
}

.checkout-title {
  font-size: 0.9rem;
  color: var(--color-text-primary);
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.checkout-circle {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.checkout-price {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-accent);
  flex-shrink: 0;
}

.checkout-total {
  display: flex;
  justify-content: space-between;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
  font-weight: 600;
}

.modal-footer {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all var(--transition-fast);
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
}

.btn-confirm {
  background: var(--color-accent);
  color: var(--color-text-primary);
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .cart-layout {
    flex-direction: column;
  }

  .cart-summary {
    width: 100%;
    position: static;
  }
}
</style>
