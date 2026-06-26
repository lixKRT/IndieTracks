import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '../stores/user.js';

// 所有路由均使用懒加载（`() => import(...)`），按需拆分 chunk
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/album/:id',
    name: 'AlbumDetail',
    component: () => import('../views/AlbumDetail.vue')
  },
  {
    path: '/labels',
    name: 'Labels',
    component: () => import('../views/Labels.vue')
  },
  {
    path: '/label/:id',
    name: 'LabelDetail',
    component: () => import('../views/LabelDetail.vue')
  },
  {
    path: '/tag',
    name: 'TagBrowse',
    component: () => import('../views/TagBrowse.vue')
  },
  {
    path: '/user/:id',
    name: 'UserProfile',
    component: () => import('../views/UserProfile.vue')
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('../views/CartView.vue')
  },
  // 管理后台路由 — 父级 meta 要求登录 + pro/staff 角色
  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, roles: ['pro', 'staff'] },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('../views/admin/Dashboard.vue')
      },
      {
        path: 'albums',
        name: 'AdminAlbumList',
        component: () => import('../views/admin/AlbumList.vue')
      },
      {
        path: 'albums/create',
        name: 'AdminAlbumCreate',
        component: () => import('../views/admin/AlbumForm.vue')
      },
      {
        path: 'albums/:id/edit',
        name: 'AdminAlbumEdit',
        component: () => import('../views/admin/AlbumForm.vue')
      },
      {
        path: 'circles',
        name: 'AdminCircleList',
        component: () => import('../views/admin/CircleList.vue'),
        // 覆盖父级角色：社团管理仅 staff 可访问
        meta: { roles: ['staff'] }
      },
      {
        path: 'circles/:id',
        name: 'AdminCircleDetail',
        component: () => import('../views/admin/CircleDetail.vue'),
        meta: { roles: ['staff'] }
      },
      {
        path: 'users',
        name: 'AdminUserList',
        component: () => import('../views/admin/UserList.vue'),
        meta: { roles: ['staff'] }
      },
      {
        path: 'tags',
        name: 'AdminTagList',
        component: () => import('../views/admin/TagList.vue')
      },
      {
        path: 'comments',
        name: 'AdminCommentList',
        component: () => import('../views/admin/CommentList.vue')
      }
    ]
  },
  // 404 兜底路由，必须放最后
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  // savedPosition 存在时说明是浏览器前进/后退，恢复之前的滚动位置
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0, behavior: 'smooth' }
  }
});

// 路由守卫 - 检查登录和角色权限
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();

  // 检查是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!userStore.isLoggedIn) {
      alert('请先登录');
      next('/');
      return;
    }

    // 检查角色权限 - 使用最具体的路由（最后一个有 roles 的）
    // matched 按父→子排列，最后一个即最内层子路由的 meta.roles
    const roleRecords = to.matched.filter(record => record.meta.roles);
    if (roleRecords.length > 0) {
      const requiredRoles = roleRecords[roleRecords.length - 1].meta.roles;
      if (!requiredRoles.includes(userStore.user?.user_role)) {
        alert('无权访问');
        next('/');
        return;
      }
    }
  }

  next();
});

export default router;
