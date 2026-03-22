<template>
  <div class="mechanic-profile-screen">
    <van-nav-bar
      title="Hồ Sơ Thợ"
      left-arrow
      @click-left="$router.back()"
      class="custom-nav-bar"
    />

    <div class="profile-content">
      <!-- Avatar + Name -->
      <div class="avatar-section">
        <div class="avatar-ring">
          <van-image
            round
            width="80"
            height="80"
            :src="avatarUrl || 'https://img.freepik.com/free-icon/user_318-159711.jpg'"
            style="object-fit:cover;"
          />
        </div>
        <h3 class="mechanic-name">{{ form.username }}</h3>
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
        <div class="gps-btn-wrap">
          <van-button
            type="primary"
            size="small"
            block
            plain
            icon="location-o"
            :loading="gpsLoading"
            loading-text="Đang lấy GPS..."
            @click="getGPS"
          >
            Cập nhật vị trí GPS
          </van-button>
        </div>
      </van-cell-group>

      <van-cell-group inset title="Thông Tin Ngân Hàng (Nhận Tiền)" class="mt-4">
        <van-field
          v-model="form.bank_name"
          label="Tên NH"
          placeholder="VD: MB, VCB, ACB..."
          left-icon="card"
        />
        <van-field
          v-model="form.bank_account_no"
          label="Số TK"
          type="number"
          placeholder="Số tài khoản"
          left-icon="points"
        />
        <van-field
          v-model="form.bank_account_name"
          label="Tên chủ thẻ"
          placeholder="VIẾT HOA KHÔNG DẤU"
          left-icon="user-circle-o"
        />
      </van-cell-group>

      <van-cell-group inset title="Trạng Thái" class="mt-4">
        <van-cell center title="Sẵn sàng nhận đơn">
          <template #right-icon>
            <van-switch v-model="form.isAvailable" size="22px" />
          </template>
        </van-cell>
        <van-cell title="Quản Lý Dịch Vụ" is-link icon="shop-o" @click="$router.push('/mechanic/services')" />
      </van-cell-group>

      <div class="save-btn-wrap">
        <van-button
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
    bank_name: '',
    bank_account_no: '',
    bank_account_name: ''
});

const avatarUrl = ref('');

const saving = ref(false);
const gpsLoading = ref(false);

onMounted(async () => {
    try {
        const res = await axios.get('/api/users/profile/');
        const user = res.data;
        form.value.username = user.username;
        form.value.phone = user.phone_number || '';
        avatarUrl.value = user.avatar || '';
        if (user.mechanic_profile) {
            form.value.specialty = user.mechanic_profile.specialty;
            form.value.latitude = user.mechanic_profile.latitude;
            form.value.longitude = user.mechanic_profile.longitude;
            form.value.isAvailable = user.mechanic_profile.is_available;
            form.value.bank_name = user.mechanic_profile.bank_name || '';
            form.value.bank_account_no = user.mechanic_profile.bank_account_no || '';
            form.value.bank_account_name = user.mechanic_profile.bank_account_name || '';
        }
    } catch(e) {
        // Fallback sang localStorage khi API lỗi báo về
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
                form.value.bank_name = user.mechanic_profile.bank_name || '';
                form.value.bank_account_no = user.mechanic_profile.bank_account_no || '';
                form.value.bank_account_name = user.mechanic_profile.bank_account_name || '';
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
        // Cập nhật trạng thái và vị trí của thợ
        await axios.post('/api/users/mechanic/status/', {
            latitude: form.value.latitude,
            longitude: form.value.longitude,
            is_available: form.value.isAvailable,
            specialty: form.value.specialty, 
            bank_name: form.value.bank_name,
            bank_account_no: form.value.bank_account_no,
            bank_account_name: form.value.bank_account_name,
        });

        // Cập nhật số điện thoại thông qua API profile
        await axios.patch('/api/users/profile/', {
            phone_number: form.value.phone,
        });

        showSuccessToast('Đã lưu hồ sơ thành công!');
        
        // Làm mới localStorage
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.mechanic-profile-screen {
  background: #f4f6f9;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  padding-bottom: 40px;
}

/* Override nav-bar */
:deep(.custom-nav-bar) {
  background: linear-gradient(135deg, #1a6fdf, #4f46e5) !important;
}
:deep(.custom-nav-bar .van-nav-bar__title) { color: #fff !important; font-weight: 700; }
:deep(.custom-nav-bar .van-icon) { color: #fff !important; }

.profile-content {
  padding: 16px;
}

/* Phần Ảnh Đại Diện */
.avatar-section {
  text-align: center;
  padding: 24px 0 20px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.avatar-ring {
  padding: 4px;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  border-radius: 50%;
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
  margin-bottom: 12px;
}
.mechanic-name {
  margin: 0 0 6px 0;
  font-size: 20px;
  font-weight: 800;
  color: #1a1a2e;
}
.role-tag {
  background: #e0eaff;
  color: #2563eb;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

/* Tùy chỉnh các Nhóm Cell & Input */
:deep(.van-cell-group--inset) {
  margin: 16px 0 0 0;
  border-radius: 16px;
  box-shadow: 0 2px 14px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}
:deep(.van-cell-group__title) {
  color: #888;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 16px 16px 8px;
}
:deep(.van-cell) {
  padding: 14px 16px;
}
:deep(.van-field__label) {
  color: #555;
  font-weight: 600;
}
:deep(.van-field__control) {
  font-weight: 600;
  color: #111;
}

.gps-btn-wrap {
  padding: 12px 16px 16px;
}

.save-btn-wrap {
  margin-top: 24px;
}

/* ─── Ghi đè Nút Bấm Hiện Đại ─── */
:deep(.van-button) {
  border-radius: 12px;
  font-weight: 700;
  border: none !important;
  transition: all 0.2s ease;
  padding: 0 16px;
  height: 44px;
}
:deep(.van-button--small) {
  border-radius: 8px;
  height: 36px;
  font-size: 13px;
}
:deep(.van-button:active) {
  transform: scale(0.97);
}
:deep(.van-button--primary:not(.van-button--plain)) {
  background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
  color: #fff !important;
  font-size: 16px;
  letter-spacing: 0.5px;
}
:deep(.van-button--primary.van-button--plain) {
  background: #eff6ff !important;
  color: #2563eb !important;
  border: 1px solid #bfdbfe !important;
  box-shadow: none;
}
/* Ghi đè giao diện nút bấm trong chế độ nền tối */
body.dark-theme :deep(.van-button--primary.van-button--plain) {
  background: #1a2744 !important;
  color: #64b5f6 !important;
  border: 1px solid #2563eb !important;
  box-shadow: none;
}
</style>
