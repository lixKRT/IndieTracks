import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
<<<<<<< HEAD
import Home from './views/Home.vue';
import Labels from './views/Labels.vue';
import AlbumDetail from './views/AlbumDetail.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/album/:id',
    name: 'AlbumDetail',
    component: AlbumDetail
  },
  {
    path: '/labels',
    name: 'Labels',
    component: Labels
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});
=======
import router from './router/index.js';

// 全局样式（按层级：变量 → 重置 → 工具类）
import './styles/tokens.css';
import './styles/reset.css';
import './styles/utilities.css';
>>>>>>> e22caadf4fa3fe0be6537cd789b14104afc5c0bc

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount('#app');
