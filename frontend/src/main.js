import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router/index.js';

// 全局样式（按层级：变量 → 重置 → 工具类）
import './styles/tokens.css';
import './styles/reset.css';
import './styles/utilities.css';

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount('#app');
