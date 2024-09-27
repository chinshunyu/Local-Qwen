import { createApp } from 'vue'
// import { createPinia } from 'pinia';
import App from './App.vue'
import { setupStore } from './store'
import 'animate.css';

const app = createApp(App)
// const pinia = createPinia();
// app.use(pinia);
setupStore(app)
app.mount('#app')
