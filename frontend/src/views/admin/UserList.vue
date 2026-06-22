<template>
  <div class="user-list-page">
    <h1 class="page-title">用户管理</h1>

    <div class="search-bar">
      <input type="text" v-model="searchQuery" placeholder="搜索用户名..." class="search-input" @keyup.enter="loadUsers" />
      <select v-model="roleFilter" class="role-filter" @change="loadUsers">
        <option value="">全部角色</option>
        <option value="normal">普通用户</option>
        <option value="pro">社团成员</option>
        <option value="staff">管理员</option>
      </select>
      <button class="btn-search" @click="loadUsers"><i class="fas fa-search"></i></button>
    </div>

    <LoadingSpinner v-if="loading" />

    <template v-else>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>头像</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>注册时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.user_id">
              <td>
                <img v-if="user.avatar_url" :src="user.avatar_url" class="user-avatar" />
                <span v-else class="avatar-placeholder"><i class="fas fa-user"></i></span>
              </td>
              <td><span class="user-name">{{ user.username }}</span></td>
              <td><span class="user-email">{{ user.email || '-' }}</span></td>
              <td>
                <span class="role-badge" :class="user.user_role">{{ roleLabel(user.user_role) }}</span>
              </td>
              <td><span class="user-date">{{ formatDate(user.created_at) }}</span></td>
              <td>
                <div class="action-buttons">
                  <button class="btn-action btn-edit" @click="editRole(user)"><i class="fas fa-edit"></i></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination" v-if="totalPages > 1">
        <button class="page-btn" :disabled="currentPage <= 1" @click="currentPage--; loadUsers()">上一页</button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="currentPage++; loadUsers()">下一页</button>
      </div>
    </template>

    <!-- 编辑角色弹窗 -->
    <Teleport to="body">
      <div v-if="editingUser" class="modal-overlay" @click.self="editingUser = null">
        <div class="modal-content">
          <div class="modal-header">
            <h3>编辑用户角色</h3>
            <button class="modal-close" @click="editingUser = null">&times;</button>
          </div>
          <div class="modal-body">
            <p class="edit-info">用户：{{ editingUser.username }}</p>
            <div class="form-group">
              <label>角色</label>
              <select v-model="editingRole">
                <option value="normal">普通用户</option>
                <option value="pro">社团成员</option>
                <option value="staff">管理员</option>
              </select>
            </div>
            <div class="form-actions">
              <button class="btn-cancel" @click="editingUser = null">取消</button>
              <button class="btn-submit" @click="saveRole">保存</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script>
import { getAdminUsers, updateUser } from '../../api/admin.js';
import LoadingSpinner from '../../components/atoms/LoadingSpinner.vue';

export default {
  name: 'AdminUserList',
  components: { LoadingSpinner },
  data() {
    return {
      users: [], loading: true, searchQuery: '', roleFilter: '',
      currentPage: 1, pageSize: 20, totalUsers: 0,
      editingUser: null, editingRole: ''
    };
  },
  computed: {
    totalPages() { return Math.ceil(this.totalUsers / this.pageSize); }
  },
  async mounted() { await this.loadUsers(); },
  methods: {
    async loadUsers() {
      this.loading = true;
      try {
        const result = await getAdminUsers({
          page: this.currentPage, page_size: this.pageSize,
          search: this.searchQuery || undefined, role: this.roleFilter || undefined
        });
        this.users = result.data || [];
        this.totalUsers = result.total || 0;
      } catch (e) { console.error('加载用户失败:', e); }
      finally { this.loading = false; }
    },
    roleLabel(role) {
      return { normal: '普通用户', pro: '社团成员', staff: '管理员' }[role] || role;
    },
    formatDate(date) {
      if (!date) return '-';
      return new Date(date).toLocaleDateString('zh-CN');
    },
    editRole(user) {
      this.editingUser = user;
      this.editingRole = user.user_role;
    },
    async saveRole() {
      try {
        await updateUser(this.editingUser.user_id, { user_role: this.editingRole });
        this.editingUser.user_role = this.editingRole;
        this.editingUser = null;
      } catch (e) {
        console.error('保存失败:', e);
        alert('保存失败');
      }
    }
  }
};
</script>

<style scoped>
.user-list-page { max-width: 1200px; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text-primary); margin-bottom: var(--spacing-xl); }
.search-bar { display: flex; gap: var(--spacing-sm); margin-bottom: var(--spacing-lg); }
.search-input { flex: 1; padding: var(--spacing-sm) var(--spacing-md); background: var(--color-bg-secondary); border: 1px solid var(--color-border); color: var(--color-text-primary); font-size: 0.9rem; }
.search-input:focus { outline: none; border-color: var(--color-accent); }
.role-filter { padding: var(--spacing-sm) var(--spacing-md); background: var(--color-bg-secondary); border: 1px solid var(--color-border); color: var(--color-text-primary); font-size: 0.9rem; }
.btn-search { padding: var(--spacing-sm) var(--spacing-md); background: var(--color-bg-secondary); border: 1px solid var(--color-border); color: var(--color-text-muted); cursor: pointer; }
.btn-search:hover { border-color: var(--color-accent); color: var(--color-accent); }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: var(--spacing-md); text-align: left; border-bottom: 1px solid var(--color-border); }
.data-table th { font-size: 0.8rem; font-weight: 600; color: var(--color-text-muted); }
.data-table tr:hover { background: rgba(255,255,255,0.02); }
.user-avatar { width: 32px; height: 32px; object-fit: cover; }
.avatar-placeholder { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: var(--color-bg-tertiary); color: var(--color-text-dim); }
.user-name { font-size: 0.9rem; color: var(--color-text-primary); }
.user-email { font-size: 0.85rem; color: var(--color-text-muted); }
.user-date { font-size: 0.8rem; color: var(--color-text-dim); }
.role-badge { padding: 2px 8px; font-size: 0.75rem; font-weight: 600; }
.role-badge.normal { background: rgba(255,255,255,0.05); color: var(--color-text-muted); }
.role-badge.pro { background: rgba(255,107,107,0.1); color: var(--color-accent); }
.role-badge.staff { background: rgba(76,175,80,0.1); color: #4caf50; }
.action-buttons { display: flex; gap: var(--spacing-sm); }
.btn-action { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; background: transparent; border: 1px solid var(--color-border); color: var(--color-text-muted); cursor: pointer; }
.btn-action:hover { border-color: var(--color-accent); color: var(--color-accent); }
.pagination { display: flex; justify-content: center; align-items: center; gap: var(--spacing-md); margin-top: var(--spacing-xl); }
.page-btn { padding: var(--spacing-sm) var(--spacing-lg); background: var(--color-bg-secondary); border: 1px solid var(--color-border); color: var(--color-text-muted); cursor: pointer; }
.page-btn:hover:not(:disabled) { border-color: var(--color-accent); color: var(--color-accent); }
.page-btn:disabled { opacity: 0.5; }
.page-info { font-size: 0.9rem; color: var(--color-text-muted); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--color-bg-secondary); border: 1px solid var(--color-border); width: 400px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--color-border); }
.modal-header h3 { font-size: 1rem; color: var(--color-text-primary); }
.modal-close { background: none; border: none; color: var(--color-text-dim); font-size: 1.2rem; cursor: pointer; }
.modal-body { padding: var(--spacing-lg); }
.edit-info { color: var(--color-text-muted); margin-bottom: var(--spacing-md); }
.form-group { margin-bottom: var(--spacing-lg); }
.form-group label { display: block; font-size: 0.85rem; color: var(--color-text-muted); margin-bottom: var(--spacing-xs); }
.form-group select { width: 100%; padding: var(--spacing-sm) var(--spacing-md); background: var(--color-bg-tertiary); border: 1px solid var(--color-border); color: var(--color-text-primary); }
.form-actions { display: flex; gap: var(--spacing-md); justify-content: flex-end; }
.btn-cancel { padding: var(--spacing-sm) var(--spacing-lg); background: transparent; border: 1px solid var(--color-border); color: var(--color-text-muted); cursor: pointer; }
.btn-submit { padding: var(--spacing-sm) var(--spacing-lg); background: var(--color-accent); border: none; color: var(--color-text-primary); font-weight: 600; cursor: pointer; }
</style>
