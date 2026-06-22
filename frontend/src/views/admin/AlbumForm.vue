<template>
  <div class="album-form-page">
    <h1 class="page-title">{{ isEdit ? '编辑专辑' : '新增专辑' }}</h1>

    <LoadingSpinner v-if="loading" />

    <form v-else @submit.prevent="handleSubmit" class="album-form">
      <div class="form-group">
        <label>标题 *</label>
        <input type="text" v-model="form.title" required placeholder="专辑标题" />
      </div>

      <div class="form-group">
        <label>封面 URL</label>
        <input type="text" v-model="form.cover_url" placeholder="封面图片地址" />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>价格</label>
          <input type="number" v-model="form.price" min="0" step="0.01" placeholder="0" />
        </div>
        <div class="form-group">
          <label>所属社团 *</label>
          <select v-model="form.circle_id" required>
            <option value="">请选择社团</option>
            <option v-for="circle in circles" :key="circle.circle_id" :value="circle.circle_id">
              {{ circle.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>内容标题</label>
        <input type="text" v-model="form.info_title" placeholder="专辑内容标题" />
      </div>

      <div class="form-group">
        <label>内容描述</label>
        <textarea v-model="form.info_content" rows="4" placeholder="专辑内容描述"></textarea>
      </div>

      <div class="form-actions">
        <router-link to="/admin/albums" class="btn-cancel">取消</router-link>
        <button type="submit" class="btn-submit" :disabled="submitting">
          {{ submitting ? '保存中...' : '保存' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { createAlbum, updateAlbum, getAdminAlbums } from '../../api/admin.js';
import { fetchCircles } from '../../api/index.js';
import { useUserStore } from '../../stores/user.js';
import LoadingSpinner from '../../components/atoms/LoadingSpinner.vue';

export default {
  name: 'AdminAlbumForm',
  components: { LoadingSpinner },
  setup() {
    const userStore = useUserStore();
    return { userStore };
  },
  data() {
    return {
      form: {
        title: '',
        cover_url: '',
        price: 0,
        circle_id: '',
        info_title: '',
        info_content: ''
      },
      circles: [],
      loading: true,
      submitting: false
    };
  },
  computed: {
    isEdit() {
      return !!this.$route.params.id;
    }
  },
  async mounted() {
    await this.loadData();
  },
  methods: {
    async loadData() {
      this.loading = true;
      try {
        // 加载社团列表
        const circleResult = await fetchCircles({ page_size: 1000 });
        this.circles = circleResult.data || [];

        // 如果是编辑模式，加载专辑数据
        if (this.isEdit) {
          const albumResult = await getAdminAlbums({ page: 1, page_size: 1 });
          const album = (albumResult.data || []).find(a => a.album_id == this.$route.params.id);
          if (album) {
            this.form = {
              title: album.title,
              cover_url: album.cover_url,
              price: album.price,
              circle_id: album.circle_id || '',
              info_title: album.info_title || '',
              info_content: album.info_content || ''
            };
          }
        }
      } catch (e) {
        console.error('加载数据失败:', e);
      } finally {
        this.loading = false;
      }
    },
    async handleSubmit() {
      this.submitting = true;
      try {
        if (this.isEdit) {
          await updateAlbum(this.$route.params.id, this.form);
          alert('专辑更新成功');
        } else {
          await createAlbum(this.form);
          alert('专辑创建成功');
        }
        this.$router.push('/admin/albums');
      } catch (e) {
        console.error('保存失败:', e);
        alert('保存失败: ' + (e.response?.data?.error || e.message));
      } finally {
        this.submitting = false;
      }
    }
  }
};
</script>

<style scoped>
.album-form-page {
  max-width: 600px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xl);
}

.album-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.form-group label {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  font-weight: 600;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  font-size: 0.9rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-accent);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.form-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
}

.btn-cancel {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-cancel:hover {
  border-color: var(--color-text-dim);
  color: var(--color-text-primary);
}

.btn-submit {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-accent);
  border: none;
  color: var(--color-text-primary);
  font-weight: 600;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.btn-submit:hover:not(:disabled) {
  background: var(--color-accent-hover);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
