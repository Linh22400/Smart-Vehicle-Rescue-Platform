import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Import router
import Vant from 'vant'
import 'vant/lib/index.css'
import axios from 'axios'

// Global Axios Config
axios.defaults.withCredentials = true;
axios.defaults.baseURL = 'http://localhost:8000';

const app = createApp(App)
app.use(router) // Use router
app.use(Vant)
app.mount('#app')
