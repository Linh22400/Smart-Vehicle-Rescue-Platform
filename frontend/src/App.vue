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
      <van-tabbar-item replace to="/mechanic" icon="manager-o" v-if="isMechanicUser()">Thợ</van-tabbar-item>
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

/* Custom UI Dark Mode Overrides */
.dark-theme .history-container, .dark-theme .history-page, .dark-theme .profile-page, .dark-theme .mechanic-profile-screen { background-color: #1c1c1e !important; }
.dark-theme .hst-card, .dark-theme .info-card, .dark-theme .menu-card, .dark-theme .edit-popup, .dark-theme .tracking-info, .dark-theme .payment-container, .dark-theme .detail-container { background-color: #2c2c2e !important; color: #f5f5f5 !important; }
.dark-theme .chat-body { background: #1c1c1e !important; }
.dark-theme .chat-header, .dark-theme .chat-footer { background: #2c2c2e !important; border-color: #444 !important; }
.dark-theme .msg-them .msg-bubble { background: #3a3a3c !important; color: #f5f5f5 !important; border-color: #555 !important; }
.dark-theme .payment-method-card { border-color: #444 !important; }
.dark-theme .menu-divider, .dark-theme .info-divider { background-color: #444 !important; }
.dark-theme .text-gray-700, .dark-theme .info-label, .dark-theme .detail-label { color: #aaa !important; }
.dark-theme .detail-value { color: #f5f5f5 !important; }
.dark-theme .tracking-title, .dark-theme .detail-title { color: #f5f5f5 !important; }
.dark-theme .chat-header h3 { color: #f5f5f5 !important; }
.dark-theme .van-popup { background: #2c2c2e !important; }
</style>
