<template>
  <div class="personal-info-screen">
    <van-nav-bar
      title="Thông tin cá nhân"
      left-arrow
      @click-left="onClickLeft"
    />
    
    <div class="p-4">
        <van-cell-group inset>
        <van-cell title="Ảnh đại diện" center>
            <template #right-icon>
            <van-image
                round
                width="40px"
                height="40px"
                src="https://img.freepik.com/free-icon/user_318-159711.jpg"
            />
            </template>
        </van-cell>
        <van-field
            v-model="user.username"
            label="Tên đăng nhập"
            readonly
        />
        <van-field
            v-model="user.email"
            label="Email"
            placeholder="Chưa cập nhật"
            readonly
        />
        <van-field
            v-model="user.phone_number"
            label="Số điện thoại"
            placeholder="Chưa cập nhật"
            readonly
        />
        <van-cell title="Vai trò" :value="user.is_mechanic ? 'Thợ sửa xe' : 'Khách hàng'" />
        </van-cell-group>
        
        <div class="mt-4 text-center">
             <van-button type="primary" plain round block disabled>Chỉnh sửa thông tin</van-button>
             <p style="font-size: 12px; color: #999; margin-top: 10px;">Tính năng chỉnh sửa đang được phát triển</p>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { showToast } from 'vant';

const router = useRouter();
const user = ref({
    username: '',
    email: '',
    phone_number: '',
    is_mechanic: false
});

onMounted(async () => {
    // Prefer live API data, fallback to localStorage
    try {
        const res = await axios.get('/api/users/profile/');
        user.value = {
            username: res.data.username || '',
            email: res.data.email || '',
            phone_number: res.data.phone_number || '',
            is_mechanic: res.data.is_mechanic || false
        };
    } catch(e) {
        // fallback to localStorage
        const savedUserStr = localStorage.getItem('user');
        if (savedUserStr) {
            try {
                const savedUser = JSON.parse(savedUserStr);
                user.value = {
                    username: savedUser.username || '',
                    email: savedUser.email || '',
                    phone_number: savedUser.phone_number || '',
                    is_mechanic: savedUser.is_mechanic || false
                };
            } catch(err) {}
        }
    }
});

const onClickLeft = () => {
    router.back();
};
</script>

<style scoped>
.personal-info-screen {
  background: #f7f8fa;
  min-height: 100vh;
}
.p-4 { padding: 16px; }
.mt-4 { margin-top: 20px; }
.text-center { text-align: center; }
</style>
