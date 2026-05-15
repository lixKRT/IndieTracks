import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import AlbumDetail from '../views/AlbumDetail.vue';
import Labels from '../views/Labels.vue';
import LabelDetail from '../views/LabelDetail.vue';
import TagBrowse from '../views/TagBrowse.vue';

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
  },
  {
    path: '/label/:id',
    name: 'LabelDetail',
    component: LabelDetail
  },
  {
    path: '/tag',
    name: 'TagBrowse',
    component: TagBrowse
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
