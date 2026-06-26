<!-- PurchaseModal — 确认购买弹窗，使用 Teleport 挂载到 body 避免 z-index 层叠问题 -->
<template>
  <!-- Teleport 挂载到 body，确保弹窗不被父级 overflow/transform 截断 -->
  <Teleport to="body">
    <!-- .self 修饰符：只在点击遮罩层本身时关闭，点击弹窗内容不触发 -->
    <div v-if="visible" class="modal-overlay" @click.self="handleClose">
      <div class="modal-content">
        <div class="modal-header">
          <h3>确认购买</h3>
          <button class="modal-close" @click="handleClose">&times;</button>
        </div>

        <div class="modal-body">
          <div class="album-info">
            <img :src="album.cover_url" :alt="album.title" class="album-cover" />
            <div class="album-details">
              <h4 class="album-title">{{ album.title }}</h4>
              <!-- 后端可能未返回 circle_name，降级显示 -->
              <p class="album-circle">{{ album.circle_name || '未知社团' }}</p>
              <!-- price 为 0 时显示免费标签 -->
              <div class="album-price">
                <span v-if="album.price > 0" class="price-paid">¥ {{ album.price }}</span>
                <span v-else class="price-free">免费</span>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <!-- purchasing 期间禁用按钮，防止重复提交 -->
          <button class="btn-cancel" @click="handleClose" :disabled="purchasing">取消</button>
          <button class="btn-confirm" @click="handleConfirm" :disabled="purchasing">
            <span v-if="purchasing" class="loading">
              <span class="spinner"></span>
              处理中...
            </span>
            <span v-else>
              {{ album.price > 0 ? `确认支付 ¥${album.price}` : '确认领取' }}
            </span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  album: { type: Object, required: true },
  visible: { type: Boolean, default: false },
  purchasing: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'confirm'])

function handleClose() {
  emit('close')
}

function handleConfirm() {
  emit('confirm')
}
</script>

<style scoped>
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
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: var(--color-text-dim);
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-close:hover {
  color: var(--color-text-primary);
}

.modal-body {
  padding: 20px;
}

.album-info {
  display: flex;
  gap: 16px;
}

.album-cover {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border: 1px solid var(--color-border);
  flex-shrink: 0;
}

.album-details {
  flex: 1;
  min-width: 0;
}

.album-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.album-circle {
  font-size: 13px;
  color: var(--color-text-muted);
  margin: 0 0 8px;
}

.album-price {
  font-size: 18px;
  font-weight: 700;
}

.price-paid {
  color: var(--color-accent);
}

.price-free {
  /* 免费标签使用 Material Green 色值，不在主题变量中 */
  color: #4caf50;
}

.modal-footer {
  display: flex;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid var(--color-border);
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
}

.btn-cancel:hover:not(:disabled) {
  border-color: var(--color-text-dim);
  color: var(--color-text-primary);
}

.btn-confirm {
  background: var(--color-accent);
  color: var(--color-text-primary);
}

.btn-confirm:hover:not(:disabled) {
  background: var(--color-accent-hover);
}

.btn-confirm:disabled {
  opacity: 0.6;
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
</style>
