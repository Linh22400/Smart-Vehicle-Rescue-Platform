<template>
  <div class="settings-screen">
    <van-nav-bar
      title="Cài đặt"
      left-arrow
      @click-left="onClickLeft"
    />
    
    <div class="p-4 mt-4">
        <van-cell-group inset title="Hệ thống">
            <van-cell center title="Nhận thông báo">
                <template #right-icon>
                    <van-switch v-model="notifications" size="24px" />
                </template>
            </van-cell>
            <van-cell center title="Giao diện tối (Dark Mode)">
                <template #right-icon>
                    <van-switch v-model="darkMode" size="24px" @change="toggleTheme" />
                </template>
            </van-cell>
            <van-cell title="Xóa bộ nhớ đệm" is-link @click="clearCache" />
        </van-cell-group>

        <van-cell-group inset title="Về ứng dụng" class="mt-4">
            <van-cell title="Phiên bản" value="1.0.0" />
            <van-cell title="Nhà phát triển" value="Smart Rescue Team" />
            <van-cell title="Điều khoản dịch vụ" is-link to="/terms" />
            <van-cell title="Chính sách bảo mật" is-link to="/privacy" />
        </van-cell-group>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { globalThemeState } from '../App.vue';

const router = useRouter();

const notifications = ref(true);
const darkMode = ref(false);

onMounted(() => {
    darkMode.value = globalThemeState.value === 'dark';
});

const toggleTheme = (checked) => {
    const newTheme = checked ? 'dark' : 'light';
    localStorage.setItem('app_theme', newTheme);
    globalThemeState.value = newTheme; // Update App's van-config-provider instantly
    
    // Dispatch to update body classes in App component
    window.dispatchEvent(new CustomEvent('theme-changed', { detail: newTheme }));
};

const onClickLeft = () => {
    router.back();
};

const clearCache = () => {
    showToast('Đã xóa bộ nhớ đệm');
};
</script>

<style scoped>
.settings-screen {
  min-height: 100vh;
}
.p-4 { padding: 16px; }
.mt-4 { margin-top: 20px; }
</style>
