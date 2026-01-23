<script setup>
// Layout wrapper
</script>

<template>
<div class="app-layout">
    <router-view />

    <van-tabbar v-if="!['/login', '/register'].includes($route.path)" route>
      <van-tabbar-item replace to="/booking" icon="location-o">Cứu Hộ</van-tabbar-item>
      <van-tabbar-item replace to="/garages" icon="shop-o">Dịch Vụ</van-tabbar-item>
      <van-tabbar-item replace to="/history" icon="orders-o">Lịch Sử</van-tabbar-item>
      <van-tabbar-item replace to="/mechanic" icon="tools">Thợ (Demo)</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style>
body { margin: 0; padding: 0; font-family: sans-serif; background: #f7f8fa; }
.app-layout { padding-bottom: 50px; }
</style>
