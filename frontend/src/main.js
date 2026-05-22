import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router/index.js';
import { useFavoriteStore } from './stores/favorite.js';

// 全局样式（按层级：变量 → 重置 → 工具类）
import './styles/tokens.css';
import './styles/reset.css';
import './styles/utilities.css';

const app = createApp(App);
const pinia = createPinia();
app.use(pinia);

// 初始化收藏 store，从 localStorage 加载数据
const favoriteStore = useFavoriteStore();
favoriteStore.initFromStorage();

app.use(router);
app.mount('#app');
