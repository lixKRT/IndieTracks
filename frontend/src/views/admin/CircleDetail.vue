<template>
  <div class="circle-detail-page">
    <div class="page-header">
      <div class="header-left">
        <router-link to="/admin/circles" class="back-link"><i class="fas fa-arrow-left"></i> 返回列表</router-link>
        <h1 class="page-title">{{ circle.name || '社团详情' }}</h1>
      </div>
      <button class="btn-delete" @click="handleDelete"><i class="fas fa-trash"></i> 删除社团</button>
    </div>

    <LoadingSpinner v-if="loading" />

    <template v-else>
      <!-- 社团信息 -->
      <div class="form-section">
        <h3 class="section-title">基本信息</h3>
        <div class="form-row">
          <div class="form-group">
            <label>Logo</label>
            <div class="logo-upload">
              <img v-if="circle.logo_url" :src="circle.logo_url" class="logo-preview" />
              <div v-else class="logo-placeholder"><i class="fas fa-image"></i></div>
              <input type="text" v-model="circle.logo_url" placeholder="Logo URL" class="logo-input" />
            </div>
          </div>
          <div class="form-group">
            <label>名称</label>
            <input type="text" v-model="circle.name" placeholder="社团名称" />
          </div>
        </div>
        <div class="form-group">
          <label>描述</label>
          <textarea v-model="circle.description" rows="4" placeholder="社团描述"></textarea>
        </div>
        <div class="form-actions">
          <button class="btn-submit" @click="saveCircle" :disabled="saving">
            {{ saving ? '保存中...' : '保存修改' }}
          </button>
        </div>
      </div>

      <!-- 成员管理 -->
      <div class="form-section">
        <h3 class="section-title">成员管理 ({{ members.length }})</h3>
        <div class="members-list">
          <div v-for="member in members" :key="member.user_id" class="member-item">
            <img v-if="member.avatar_url" :src="member.avatar_url" class="member-avatar" />
            <span v-else class="member-avatar-placeholder"><i class="fas fa-user"></i></span>
            <div class="member-info">
              <span class="member-name">{{ member.username }}</span>
              <span class="member-role">{{ member.user_role }}</span>
            </div>
            <button class="btn-remove" @click="removeMember(member)" title="移除"><i class="fas fa-times"></i></button>
          </div>
          <div v-if="members.length === 0" class="no-members">暂无成员</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { getAdminCircles } from '../../api/admin.js';
import LoadingSpinner from '../../components/atoms/LoadingSpinner.vue';

export default {
  name: 'AdminCircleDetail',
  components: { LoadingSpinner },
  data() {
    return {
      circle: {},
      members: [],
      loading: true,
      saving: false
    };
  },
  async mounted() {
    await this.loadCircle();
  },
  methods: {
    async loadCircle() {
      this.loading = true;
      try {
        const id = this.$route.params.id;
        const resp = await fetch(`/api/admin/circles/${id}`, { credentials: 'include' });
        const data = await resp.json();
        this.circle = {
          circle_id: data.circle_id,
          name: data.name || '',
          logo_url: data.logo_url || '',
          description: data.description || ''
        };
        this.members = data.members || [];
      } catch (e) { console.error('加载社团失败:', e); }
      finally { this.loading = false; }
    },
    async saveCircle() {
      this.saving = true;
      try {
        const resp = await fetch(`/api/admin/circles/${this.circle.circle_id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(this.circle)
        });
        if (resp.ok) alert('保存成功');
        else alert('保存失败');
      } catch (e) { console.error('保存失败:', e); alert('保存失败'); }
      finally { this.saving = false; }
    },
    async handleDelete() {
      if (!confirm(`确定删除社团「${this.circle.name}」？此操作不可恢复！`)) return;
      try {
        const resp = await fetch(`/api/admin/circles/${this.circle.circle_id}`, {
          method: 'DELETE', credentials: 'include'
        });
        if (resp.ok) {
          alert('删除成功');
          this.$router.push('/admin/circles');
        }
      } catch (e) { console.error('删除失败:', e); alert('删除失败'); }
    },
    async removeMember(member) {
      if (!confirm(`确定移除成员「${member.username}」？`)) return;
      try {
        const resp = await fetch(`/api/admin/circles/${this.circle.circle_id}/members/${member.user_id}`, {
          method: 'DELETE', credentials: 'include'
        });
        if (resp.ok) {
          this.members = this.members.filter(m => m.user_id !== member.user_id);
        }
      } catch (e) { console.error('移除失败:', e); alert('移除失败'); }
    }
  }
};
</script>

<style scoped>
.circle-detail-page { max-width: 900px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-xl); }
.header-left { display: flex; align-items: center; gap: var(--spacing-md); }
.back-link { color: var(--color-text-muted); text-decoration: none; font-size: 0.9rem; }
.back-link:hover { color: var(--color-accent); }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text-primary); }
.btn-delete { padding: var(--spacing-sm) var(--spacing-lg); background: transparent; border: 1px solid #e53935; color: #e53935; cursor: pointer; font-size: 0.85rem; display: flex; align-items: center; gap: var(--spacing-sm); }
.btn-delete:hover { background: #e53935; color: var(--color-text-primary); }
.form-section { background: var(--color-bg-secondary); border: 1px solid var(--color-border); padding: var(--spacing-lg); margin-bottom: var(--spacing-lg); }
.section-title { font-size: 1rem; font-weight: 600; color: var(--color-text-primary); margin-bottom: var(--spacing-lg); padding-bottom: var(--spacing-sm); border-bottom: 1px solid var(--color-border); }
.form-group { display: flex; flex-direction: column; gap: var(--spacing-xs); margin-bottom: var(--spacing-md); }
.form-group label { font-size: 0.85rem; color: var(--color-text-muted); font-weight: 600; }
.form-group input, .form-group textarea { padding: var(--spacing-sm) var(--spacing-md); background: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary); font-size: 0.9rem; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: var(--color-accent); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.logo-upload { display: flex; gap: var(--spacing-md); align-items: center; }
.logo-preview { width: 80px; height: 80px; object-fit: cover; border: 1px solid var(--color-border); }
.logo-placeholder { width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; background: var(--color-bg-tertiary); border: 1px dashed var(--color-border); color: var(--color-text-dim); font-size: 1.5rem; }
.logo-input { flex: 1; }
.form-actions { display: flex; justify-content: flex-end; margin-top: var(--spacing-md); }
.btn-submit { padding: var(--spacing-sm) var(--spacing-lg); background: var(--color-accent); border: none; color: var(--color-text-primary); font-weight: 600; cursor: pointer; }
.btn-submit:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn-submit:disabled { opacity: 0.5; }
.members-list { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.member-item { display: flex; align-items: center; gap: var(--spacing-md); padding: var(--spacing-sm); border-bottom: 1px solid var(--color-border); }
.member-avatar { width: 36px; height: 36px; object-fit: cover; }
.member-avatar-placeholder { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background: var(--color-bg-tertiary); color: var(--color-text-dim); }
.member-info { flex: 1; }
.member-name { font-size: 0.9rem; color: var(--color-text-primary); }
.member-role { font-size: 0.75rem; color: var(--color-text-muted); margin-left: var(--spacing-sm); }
.btn-remove { width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; background: transparent; border: 1px solid var(--color-border); color: var(--color-text-muted); cursor: pointer; }
.btn-remove:hover { border-color: #e53935; color: #e53935; }
.no-members { font-size: 0.85rem; color: var(--color-text-dim); text-align: center; padding: var(--spacing-lg); }
</style>
