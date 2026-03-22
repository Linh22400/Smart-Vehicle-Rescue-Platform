<template>
  <div class="personal-info-screen">
    <van-nav-bar
      title="Thông tin cá nhân"
      left-arrow
      @click-left="router.back()"
      :right-text="editMode ? 'Lưu' : 'Sửa'"
      @click-right="editMode ? saveInfo() : (editMode = true)"
    />

    <div class="p-4">
      <van-cell-group inset>
        <van-cell title="Ảnh đại diện" center>
          <template #right-icon>
            <van-image round width="40px" height="40px"
              :src="user.avatar || 'https://img.freepik.com/free-icon/user_318-159711.jpg'" />
          </template>
        </van-cell>
        <van-field v-model="user.username" label="Tên đăng nhập" readonly />
        <van-field
          v-model="user.email" label="Email"
          placeholder="Chưa cập nhật"
          :readonly="!editMode"
          type="email"
        />
        <van-field
          v-model="user.phone_number" label="Số điện thoại"
          placeholder="Chưa cập nhật"
          :readonly="!editMode"
          type="tel"
        />
        <van-field
          v-if="editMode" v-model="user.first_name" label="Họ"
          placeholder="Họ của bạn"
        />
        <van-field
          v-if="editMode" v-model="user.last_name" label="Tên"
          placeholder="Tên của bạn"
        />
        <van-cell title="Vai trò" :value="user.is_mechanic ? 'Thợ sửa xe' : 'Khách hàng'" />
      </van-cell-group>

      <van-button v-if="editMode" class="mt-4" type="primary" round block
        :loading="saving" @click="saveInfo">
        💾 Lưu thay đổi
      </van-button>
      <van-button v-if="editMode" class="mt-2" plain round block @click="cancelEdit">
        Hủy
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { showSuccessToast, showFailToast } from 'vant';

const router = useRouter();
const editMode = ref(false);
const saving = ref(false);
const originalUser = ref({});
const user = ref({
  username: '', email: '', phone_number: '',
  first_name: '', last_name: '', is_mechanic: false, avatar: ''
});

onMounted(async () => {
  try {
    const res = await axios.get('/api/users/profile/');
    user.value = { ...user.value, ...res.data };
    originalUser.value = { ...user.value };
  } catch(e) {
    const saved = localStorage.getItem('user');
    if (saved) {
      try { user.value = { ...user.value, ...JSON.parse(saved) }; } catch {}
    }
  }
});

const cancelEdit = () => {
  user.value = { ...originalUser.value };
  editMode.value = false;
};

const saveInfo = async () => {
  saving.value = true;
  try {
    const res = await axios.patch('/api/users/profile/', {
      email: user.value.email,
      phone_number: user.value.phone_number,
      first_name: user.value.first_name,
      last_name: user.value.last_name,
    });
    originalUser.value = { ...user.value, ...res.data };
    user.value = { ...originalUser.value };
    // Đồng bộ với cache localStorage
    const stored = JSON.parse(localStorage.getItem('user') || '{}');
    localStorage.setItem('user', JSON.stringify({ ...stored, ...res.data }));
    showSuccessToast('Đã lưu thông tin!');
    editMode.value = false;
  } catch(e) {
    showFailToast(e.response?.data?.error || 'Lỗi lưu thông tin');
  } finally {
    saving.value = false;
  }
};
</script>

<style scoped>
.personal-info-screen { background: #f7f8fa; min-height: 100vh; }
.p-4 { padding: 16px; }
.mt-4 { margin-top: 16px; }
.mt-2 { margin-top: 8px; }
</style>
