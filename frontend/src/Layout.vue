<template>
  <div class="app-layout">
    <router-view />
    
    <!-- Hide Bottom Bar on Login/Register -->
    <van-tabbar v-if="showBottomBar" route>
      <van-tabbar-item replace to="/booking" icon="location-o">Đặt Xe</van-tabbar-item>
      
      <van-tabbar-item v-if="isMechanic" replace to="/mechanic" icon="tools">Thợ</van-tabbar-item>
      <van-tabbar-item v-else replace to="/history" icon="orders-o">Lịch Sử</van-tabbar-item>
      
      <van-tabbar-item replace to="/login" icon="setting-o">Thoát</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const isMechanic = ref(false);

const showBottomBar = computed(() => {
    return !['/login', '/register'].includes(route.path);
});

onMounted(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        const user = JSON.parse(userStr);
        isMechanic.value = user.is_mechanic;
    }
});
</script>
