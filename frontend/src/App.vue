<script setup>
// Layout wrapper
</script>

<template>
<van-config-provider :theme="themeClass">
<div class="app-layout" :class="themeClass">
    <router-view />

    <van-tabbar v-if="!['/login', '/register'].includes($route.path)" route>
      <van-tabbar-item replace to="/booking" icon="location-o">Cứu Hộ</van-tabbar-item>
      <van-tabbar-item replace to="/garages" icon="shop-o">Dịch Vụ</van-tabbar-item>
      <van-tabbar-item replace to="/history" icon="orders-o">Lịch Sử</van-tabbar-item>
      <van-tabbar-item replace to="/mechanic" icon="tools" v-if="isMechanicUser()">Thợ</van-tabbar-item>
      <van-tabbar-item replace to="/profile" icon="user-o">Tài Khoản</van-tabbar-item>
    </van-tabbar>
  </div>
</van-config-provider>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';

// Use a shared reactive state so SettingsScreen can mutate it without reloads
export const globalThemeState = ref(localStorage.getItem('app_theme') || 'light');

export default {
  setup() {
    
    const applyTheme = (val) => {
        if (val === 'dark') {
            document.body.classList.add('dark-theme');
            document.body.style.background = '#1c1c1e';
        } else {
            document.body.classList.remove('dark-theme');
            document.body.style.background = '#f7f8fa';
        }
    }

    onMounted(() => {
        // Apply theme on load
        applyTheme(globalThemeState.value);
        
        // Listen for storage changes from other tabs if needed
        window.addEventListener('theme-changed', (e) => {
            applyTheme(e.detail);
        });
    });

    onUnmounted(() => {
        window.removeEventListener('theme-changed', () => {});
    });

    return {
      themeClass: globalThemeState
    }
  },
  methods: {
    isMechanicUser() {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          return user.is_mechanic;
        } catch(e) {}
      }
      return false;
    }
  }
}
</script>

<style>
body { margin: 0; padding: 0; font-family: sans-serif; transition: background 0.3s, color 0.3s; }
.app-layout { padding-bottom: 50px; min-height: 100vh; }

/* Dark Theme Overrides for Custom Elements (Vant handles most via ConfigProvider and theme="dark") */
body.dark-theme, .app-layout.dark { 
    background: #1c1c1e !important; 
    color: #f5f5f5; 
}
.dark-theme .revenue-card,
.dark-theme .chart-mock,
.dark-theme .map-header,
.dark-theme .user-info,
.dark-theme .login-container {
    background-color: #2c2c2e !important;
    color: #f5f5f5 !important;
}
.dark-theme .revenue-card h3,
.dark-theme .chart-mock p,
.dark-theme .mt-1 {
    color: #aaa !important;
}
.dark-theme .van-nav-bar, 
.dark-theme .van-cell, 
.dark-theme .van-cell-group, 
.dark-theme .van-tabbar {
    background-color: #1c1c1e !important;
}
</style>
