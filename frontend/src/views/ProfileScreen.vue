<template>
  <div class="profile-screen">
    <van-nav-bar title="Tài Khoản" />
    
    <div class="user-info p-4 text-center mt-4">
      <van-image
        round
        width="100px"
        height="100px"
        src="https://img.freepik.com/free-icon/user_318-159711.jpg"
      />
      <h2 class="mt-2">{{ username }}</h2>
      <van-tag :type="isMechanic ? 'danger' : 'primary'" size="medium" class="mt-1">
        {{ isMechanic ? 'Thợ sửa xe' : 'Khách hàng' }}
      </van-tag>
    </div>

    <van-cell-group inset class="mt-4">
      <van-cell title="Thông tin cá nhân" icon="contact-o" is-link to="/profile/info" />
      <van-cell v-if="isMechanic" title="Trang tổng quan Thợ" icon="tools-o" is-link to="/mechanic" />
      <van-cell title="Lịch sử hoạt động" icon="clock-o" is-link to="/history" />
      <van-cell title="Cài đặt" icon="setting-o" is-link to="/settings" />
      <van-cell title="Đăng Xuất" icon="close" @click="handleLogout" style="color: red; text-align: center; font-weight: bold; justify-content: center;" />
    </van-cell-group>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { showToast, showSuccessToast, showFailToast } from 'vant';

const router = useRouter();
const username = ref('Đang tải...');
const isMechanic = ref(false);

onMounted(() => {
    const savedUserStr = localStorage.getItem('user');
    if (savedUserStr) {
        const savedUser = JSON.parse(savedUserStr);
        username.value = savedUser.username;
        isMechanic.value = savedUser.is_mechanic;
    } else {
        username.value = "Người dùng";
    }
});

const handleLogout = async () => {
    try {
        await axios.post('/api/users/logout/');
        localStorage.removeItem('user');
        showSuccessToast('Đã đăng xuất');
        router.push('/login');
    } catch (e) {
        showFailToast('Lỗi đăng xuất');
        router.push('/login'); // Still push to login on error just in case
    }
}
</script>

<style scoped>
.profile-screen {
  background: #f7f8fa;
  min-height: 100vh;
  padding-bottom: 60px;
}
.p-4 { padding: 16px; }
.text-center { text-align: center; }
.mt-4 { margin-top: 20px; }
.mt-2 { margin-top: 10px; }
.mt-1 { margin-top: 5px; }
</style>
