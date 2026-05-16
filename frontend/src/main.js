import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
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

const app = createApp(App);
app.use(router);
app.mount('#app');
