<template>
  <div class="mechanic-profile-screen">
    <van-nav-bar
      title="Hồ Sơ Thợ"
      left-arrow
      @click-left="$router.back()"
    />

    <div class="p-4">
      <!-- Avatar + Name -->
      <div class="avatar-section">
        <van-image
          round
          width="80"
          height="80"
          src="https://img.freepik.com/free-icon/user_318-159711.jpg"
        />
        <h3>{{ form.username }}</h3>
        <span class="role-tag">Thợ Cứu Hộ</span>
      </div>

      <van-cell-group inset title="Thông Tin Cơ Bản" class="mt-4">
        <van-field
          v-model="form.specialty"
          label="Chuyên môn"
          placeholder="Ví dụ: Sửa điện, Vá lốp..."
          left-icon="certificate"
        />
        <van-field
          v-model="form.phone"
          label="Số ĐT"
          type="tel"
          placeholder="Số điện thoại"
          left-icon="phone-o"
        />
      </van-cell-group>

      <van-cell-group inset title="Vị Trí Hiện Tại" class="mt-4">
        <van-cell title="Latitude" :value="form.latitude ? form.latitude.toFixed(5) : 'Chưa cập nhật'" />
        <van-cell title="Longitude" :value="form.longitude ? form.longitude.toFixed(5) : 'Chưa cập nhật'" />
        <div class="p-2">
          <van-button
            type="primary"
            size="small"
            block
            plain
            :loading="gpsLoading"
            @click="getGPS"
          >
            📍 Cập nhật vị trí GPS
          </van-button>
        </div>
      </van-cell-group>

      <van-cell-group inset title="Trạng Thái" class="mt-4">
        <van-cell center title="Sẵn sàng nhận đơn">
          <template #right-icon>
            <van-switch v-model="form.isAvailable" size="22px" />
          </template>
        </van-cell>
      </van-cell-group>

      <div class="mt-4">
        <van-button
          round
          block
          type="primary"
          :loading="saving"
          @click="saveProfile"
        >
          Lưu Hồ Sơ
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { showSuccessToast, showFailToast, showToast } from 'vant';

const form = ref({
    username: '',
    specialty: '',
    phone: '',
    latitude: null,
    longitude: null,
    isAvailable: true,
});

const saving = ref(false);
const gpsLoading = ref(false);

onMounted(async () => {
    try {
        const res = await axios.get('/api/users/profile/');
        const user = res.data;
        form.value.username = user.username;
        form.value.phone = user.phone_number || '';
        if (user.mechanic_profile) {
            form.value.specialty = user.mechanic_profile.specialty;
            form.value.latitude = user.mechanic_profile.latitude;
            form.value.longitude = user.mechanic_profile.longitude;
            form.value.isAvailable = user.mechanic_profile.is_available;
        }
    } catch(e) {
        // Fallback to localStorage
        const savedStr = localStorage.getItem('user');
        if (savedStr) {
            const user = JSON.parse(savedStr);
            form.value.username = user.username;
            form.value.phone = user.phone_number || '';
            if (user.mechanic_profile) {
                form.value.specialty = user.mechanic_profile.specialty || '';
                form.value.latitude = user.mechanic_profile.latitude;
                form.value.longitude = user.mechanic_profile.longitude;
                form.value.isAvailable = user.mechanic_profile.is_available;
            }
        }
    }
});

const getGPS = () => {
    if (!navigator.geolocation) {
        showToast('Trình duyệt không hỗ trợ GPS');
        return;
    }
    gpsLoading.value = true;
    navigator.geolocation.getCurrentPosition(
        pos => {
            form.value.latitude = pos.coords.latitude;
            form.value.longitude = pos.coords.longitude;
            gpsLoading.value = false;
            showSuccessToast('Đã lấy vị trí GPS!');
        },
        err => {
            gpsLoading.value = false;
            showFailToast('Không lấy được GPS');
        }
    );
};

const saveProfile = async () => {
    saving.value = true;
    try {
        // Update mechanic status and location
        await axios.post('/api/users/mechanic/status/', {
            latitude: form.value.latitude,
            longitude: form.value.longitude,
            is_available: form.value.isAvailable,
            specialty: form.value.specialty, 
        });

        // Update phone via profile API
        await axios.patch('/api/users/profile/', {
            phone_number: form.value.phone,
        });

        showSuccessToast('Đã lưu hồ sơ thành công!');
        
        // Refresh localStorage
        const res = await axios.get('/api/users/profile/');
        localStorage.setItem('user', JSON.stringify(res.data));
    } catch(e) {
        console.error(e);
        showFailToast('Lỗi lưu hồ sơ');
    } finally {
        saving.value = false;
    }
};
</script>

<style scoped>
.mechanic-profile-screen {
    background: #f7f8fa;
    min-height: 100vh;
}
.avatar-section {
    text-align: center;
    padding: 20px 0 10px 0;
}
.avatar-section h3 {
    margin: 10px 0 4px 0;
    font-size: 18px;
}
.role-tag {
    background: #1989fa;
    color: white;
    padding: 2px 12px;
    border-radius: 12px;
    font-size: 12px;
}
.p-4 { padding: 16px; }
.p-2 { padding: 8px; }
.mt-4 { margin-top: 16px; }
</style>
