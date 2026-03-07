<template>
  <div class="app-layout">
    <router-view />
    
    <!-- Hide Bottom Bar on Login/Register -->
    <van-tabbar v-if="showBottomBar" route>
      <!-- Tab 1: Trang chủ / Đặt xe (both roles) -->
      <van-tabbar-item replace to="/booking" icon="wap-home-o">Trang chủ</van-tabbar-item>
      
      <!-- Tab 2: Role-specific -->
      <van-tabbar-item v-if="isMechanic" replace to="/mechanic" icon="todo-list-o">Dashboard</van-tabbar-item>
      <van-tabbar-item v-else replace to="/garages" icon="shop-o">Dịch vụ</van-tabbar-item>

      <!-- Tab 3: Lịch sử (both roles) -->
      <van-tabbar-item replace to="/history" icon="orders-o">Lịch sử</van-tabbar-item>
      
      <!-- Tab 4: Hồ sơ (both roles) -->
      <van-tabbar-item replace to="/profile" icon="contact-o">Hồ sơ</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const isMechanic = ref(false);

const showBottomBar = computed(() => {
    return !['/login', '/register'].includes(route.path);
});

// Re-read user info on route change (in case they just logged in)
const loadUserInfo = () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            isMechanic.value = !!user.is_mechanic;
        } catch (e) { }
    }
};

onMounted(loadUserInfo);
watch(() => route.path, loadUserInfo);
</script>
