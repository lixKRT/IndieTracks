import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '../stores/user.js';

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
  // 管理后台路由
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
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
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

    // 检查角色权限
    const requiredRoles = to.matched.find(record => record.meta.roles)?.meta.roles;
    if (requiredRoles && !requiredRoles.includes(userStore.user?.user_role)) {
      alert('无权访问');
      next('/');
      return;
    }
  }

  next();
});

export default router;
