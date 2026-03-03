<template>
  <div class="profile-page">

    <!-- Hero Banner -->
    <div class="profile-hero">
      <div class="hero-bg-circle"></div>
      <div class="profile-avatar-wrap">
        <van-image round width="84px" height="84px"
          src="https://img.freepik.com/free-icon/user_318-159711.jpg"
          class="profile-avatar" />
        <div v-if="isMechanic" class="avatar-badge">Thợ</div>
      </div>
      <div class="profile-name">{{ displayName }}</div>
      <div class="profile-role-chip" :class="isMechanic ? 'chip-mechanic' : 'chip-customer'">
        <van-icon :name="isMechanic ? 'manager-o' : 'friends-o'" size="12" />
        {{ isMechanic ? 'Thợ Sửa Xe' : 'Khách Hàng' }}
      </div>
    </div>

    <!-- Info Summary Card -->
    <div class="info-card">
      <div class="info-row">
        <div class="info-icon-wrap blue"><van-icon name="contact-o" size="14" color="#fff" /></div>
        <div class="info-content">
          <div class="info-label">Tên đầy đủ</div>
          <div class="info-value">{{ fullName || username }}</div>
        </div>
      </div>
      <div class="info-divider"></div>
      <div class="info-row">
        <div class="info-icon-wrap green"><van-icon name="phone-o" size="14" color="#fff" /></div>
        <div class="info-content">
          <div class="info-label">Số điện thoại</div>
          <div class="info-value">{{ phoneNumber || 'Chưa cập nhật' }}</div>
        </div>
      </div>
      <div class="info-divider"></div>
      <div class="info-row">
        <div class="info-icon-wrap purple"><van-icon name="envelop-o" size="14" color="#fff" /></div>
        <div class="info-content">
          <div class="info-label">Email</div>
          <div class="info-value">{{ email || 'Chưa cập nhật' }}</div>
        </div>
      </div>
      <div class="info-divider"></div>
      <div class="info-row">
        <div class="info-icon-wrap gray"><van-icon name="user-o" size="14" color="#fff" /></div>
        <div class="info-content">
          <div class="info-label">Tên đăng nhập</div>
          <div class="info-value">{{ username }}</div>
        </div>
      </div>
    </div>

    <!-- Edit Button -->
    <div class="edit-btn-wrap">
      <button class="edit-btn" @click="openEdit">
        <van-icon name="edit" size="15" />
        Chỉnh sửa thông tin
      </button>
    </div>

    <!-- Menu Cards -->
    <div class="menu-section">
      <div class="menu-group-label">Chức năng</div>
      <div class="menu-card">
        <div v-if="isMechanic" class="menu-item" @click="$router.push('/mechanic')">
          <div class="menu-item-icon purple"><van-icon name="manager-o" size="18" /></div>
          <span class="menu-item-label">Trang tổng quan Thợ</span>
          <van-icon name="arrow" size="14" color="#ccc" />
        </div>
        <div v-if="isMechanic" class="menu-divider"></div>
        <div class="menu-item" @click="$router.push('/history')">
          <div class="menu-item-icon green"><van-icon name="orders-o" size="18" /></div>
          <span class="menu-item-label">Lịch sử hoạt động</span>
          <van-icon name="arrow" size="14" color="#ccc" />
        </div>
      </div>

      <!-- Logout -->
      <div class="logout-btn" @click="handleLogout">
        <van-icon name="close-o" size="16" />
        Đăng Xuất
      </div>
    </div>

    <!-- ── Edit Profile Popup ── -->
    <van-popup v-model:show="editVisible" position="bottom"
      round :style="{ maxHeight: '90%', overflowY: 'auto' }">
      <div class="edit-popup">
        <div class="edit-popup-header">
          <span class="edit-popup-title">Chỉnh sửa thông tin</span>
          <van-icon name="cross" size="18" color="#888" @click="editVisible = false" />
        </div>

        <!-- Section: Basic info -->
        <div class="ep-section-label">
          <div class="ep-dot blue"></div>Thông tin cơ bản
        </div>

        <div class="ep-field">
          <div class="ep-field-label">Họ</div>
          <input v-model="form.last_name" class="ep-input" placeholder="Nguyễn" />
        </div>
        <div class="ep-field">
          <div class="ep-field-label">Tên</div>
          <input v-model="form.first_name" class="ep-input" placeholder="Văn A" />
        </div>
        <div class="ep-field">
          <div class="ep-field-label">Số điện thoại</div>
          <input v-model="form.phone_number" class="ep-input" placeholder="0901234567" type="tel" />
        </div>
        <div class="ep-field">
          <div class="ep-field-label">Email</div>
          <input v-model="form.email" class="ep-input" placeholder="example@email.com" type="email" />
        </div>

        <!-- Section: Change password -->
        <div class="ep-section-label" style="margin-top: 20px">
          <div class="ep-dot red"></div>Đổi mật khẩu (tuỳ chọn)
        </div>

        <div class="ep-field">
          <div class="ep-field-label">Mật khẩu hiện tại</div>
          <div class="ep-input-wrap">
            <input v-model="form.current_password" class="ep-input"
              :type="showCurrentPw ? 'text' : 'password'"
              placeholder="Nhập mật khẩu hiện tại" />
            <van-icon :name="showCurrentPw ? 'eye-o' : 'closed-eye'"
              size="18" color="#aaa" @click="showCurrentPw = !showCurrentPw" />
          </div>
        </div>
        <div class="ep-field">
          <div class="ep-field-label">Mật khẩu mới</div>
          <div class="ep-input-wrap">
            <input v-model="form.new_password" class="ep-input"
              :type="showNewPw ? 'text' : 'password'"
              placeholder="Tối thiểu 6 ký tự" />
            <van-icon :name="showNewPw ? 'eye-o' : 'closed-eye'"
              size="18" color="#aaa" @click="showNewPw = !showNewPw" />
          </div>
        </div>

        <!-- Save button -->
        <button class="ep-save-btn" :disabled="saving" @click="saveProfile">
          <van-loading v-if="saving" size="16" color="#fff" />
          <span v-else><van-icon name="success" size="14" /> Lưu thay đổi</span>
        </button>
      </div>
    </van-popup>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { showSuccessToast, showFailToast } from 'vant';

const router = useRouter();

// ─── User State ──────────────────────────────────────────────────
const username    = ref('');
const firstName   = ref('');
const lastName    = ref('');
const email       = ref('');
const phoneNumber = ref('');
const isMechanic  = ref(false);

const displayName = computed(() =>
  (firstName.value || lastName.value)
    ? `${lastName.value} ${firstName.value}`.trim()
    : username.value || 'Người dùng'
);
const fullName = computed(() =>
  (firstName.value || lastName.value)
    ? `${lastName.value} ${firstName.value}`.trim()
    : ''
);

// ─── Edit Popup State ─────────────────────────────────────────────
const editVisible   = ref(false);
const saving        = ref(false);
const showCurrentPw = ref(false);
const showNewPw     = ref(false);
const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone_number: '',
  current_password: '',
  new_password: '',
});

const openEdit = () => {
  form.value = {
    first_name:       firstName.value,
    last_name:        lastName.value,
    email:            email.value,
    phone_number:     phoneNumber.value,
    current_password: '',
    new_password:     '',
  };
  showCurrentPw.value = false;
  showNewPw.value = false;
  editVisible.value = true;
};

// ─── Load Profile ─────────────────────────────────────────────────
const loadProfile = async () => {
  // Pre-fill from localStorage instantly
  const saved = localStorage.getItem('user');
  if (saved) {
    const u = JSON.parse(saved);
    username.value    = u.username    || '';
    firstName.value   = u.first_name  || '';
    lastName.value    = u.last_name   || '';
    email.value       = u.email       || '';
    phoneNumber.value = u.phone_number|| '';
    isMechanic.value  = u.is_mechanic || false;
  }
  // Fetch fresh data from server
  try {
    const res = await axios.get('/api/users/profile/');
    const u = res.data;
    username.value    = u.username     || '';
    firstName.value   = u.first_name   || '';
    lastName.value    = u.last_name    || '';
    email.value       = u.email        || '';
    phoneNumber.value = u.phone_number || '';
    isMechanic.value  = u.is_mechanic  || false;
    localStorage.setItem('user', JSON.stringify(u));
  } catch (_) { /* keep localStorage values */ }
};

// ─── Save Profile ─────────────────────────────────────────────────
const saveProfile = async () => {
  saving.value = true;
  try {
    const payload = {
      first_name:   form.value.first_name,
      last_name:    form.value.last_name,
      email:        form.value.email,
      phone_number: form.value.phone_number,
    };
    if (form.value.new_password) {
      payload.current_password = form.value.current_password;
      payload.new_password     = form.value.new_password;
    }
    const res = await axios.patch('/api/users/profile/', payload);
    const u = res.data;
    firstName.value   = u.first_name   || '';
    lastName.value    = u.last_name    || '';
    email.value       = u.email        || '';
    phoneNumber.value = u.phone_number || '';
    const stored = JSON.parse(localStorage.getItem('user') || '{}');
    localStorage.setItem('user', JSON.stringify({ ...stored, ...u }));
    showSuccessToast('Cập nhật thành công!');
    editVisible.value = false;
  } catch (e) {
    const msg = e.response?.data?.error || 'Lỗi cập nhật thông tin';
    showFailToast(msg);
  } finally {
    saving.value = false;
  }
};

// ─── Logout ───────────────────────────────────────────────────────
const handleLogout = async () => {
  try {
    await axios.post('/api/users/logout/');
    localStorage.removeItem('user');
    showSuccessToast('Đã đăng xuất');
    router.push('/login');
  } catch (_) {
    router.push('/login');
  }
};

onMounted(loadProfile);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

.profile-page {
  min-height: 100vh;
  background: #f3f4f8;
  font-family: 'Inter', sans-serif;
  padding-bottom: 80px;
}

/* ── Hero ── */
.profile-hero {
  background: linear-gradient(145deg, #1a6fdf, #4f46e5);
  padding: 40px 20px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow: hidden;
}
.hero-bg-circle {
  position: absolute;
  width: 260px; height: 260px;
  border-radius: 50%;
  background: rgba(255,255,255,0.07);
  top: -80px; right: -70px;
}
.profile-avatar-wrap { position: relative; margin-bottom: 12px; }
.profile-avatar { border: 3px solid rgba(255,255,255,0.7); box-shadow: 0 6px 20px rgba(0,0,0,0.2); }
.avatar-badge {
  position: absolute; bottom: 2px; right: -2px;
  background: #f5a623; color: #fff; font-size: 10px; font-weight: 700;
  border-radius: 8px; padding: 2px 6px; border: 2px solid #fff;
}
.profile-name { color: #fff; font-size: 20px; font-weight: 700; margin-bottom: 8px; }
.profile-role-chip {
  display: flex; align-items: center; gap: 5px;
  padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 600;
}
.chip-mechanic { background: rgba(245,166,35,0.25); color: #fde68a; }
.chip-customer { background: rgba(255,255,255,0.2); color: rgba(255,255,255,0.9); }

/* ── Info Card ── */
.info-card {
  background: #fff;
  border-radius: 16px;
  margin: 14px 14px 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  overflow: hidden;
}
.info-row { display: flex; align-items: center; gap: 12px; padding: 13px 16px; }
.info-icon-wrap {
  width: 30px; height: 30px; border-radius: 9px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.info-content { flex: 1; min-width: 0; }
.info-label { font-size: 11px; color: #aaa; font-weight: 600; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.4px; }
.info-value { font-size: 14px; font-weight: 600; color: #1a1a2e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.info-divider { height: 1px; background: #f3f4f8; margin: 0 16px; }

/* ── Edit Button ── */
.edit-btn-wrap { padding: 12px 14px 0; }
.edit-btn {
  width: 100%; height: 44px; display: flex; align-items: center; justify-content: center; gap: 8px;
  background: linear-gradient(90deg, #2563eb, #4f46e5);
  color: #fff; border: none; border-radius: 12px;
  font-size: 14px; font-weight: 700; cursor: pointer;
  box-shadow: 0 3px 12px rgba(37,99,235,0.3);
  transition: opacity 0.15s;
}
.edit-btn:active { opacity: 0.88; }

/* ── Menu section ── */
.menu-section { padding: 16px 14px 0; }
.menu-group-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; color: #aaa; font-weight: 700; margin: 0 4px 10px; }
.menu-card { background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.06); margin-bottom: 16px; }
.menu-item { display: flex; align-items: center; padding: 14px 16px; cursor: pointer; transition: background 0.15s; gap: 14px; }
.menu-item:active { background: #f9f9f9; }
.menu-item-icon { width: 34px; height: 34px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: #fff; }
.blue   { background: #2563eb; }
.purple { background: #7c3aed; }
.green  { background: #059669; }
.gray   { background: #6b7280; }
.red    { background: #e03131; }
.menu-item-label { flex: 1; font-size: 14px; font-weight: 500; color: #1a1a2e; }
.menu-divider { height: 1px; background: #f3f4f8; margin: 0 16px; }

.logout-btn {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  background: #fff; border-radius: 14px; padding: 14px;
  font-size: 14px; font-weight: 700; color: #e03131;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06); cursor: pointer;
  transition: background 0.15s;
}
.logout-btn:active { background: #fff5f5; }

/* ── Edit Popup ── */
.edit-popup { padding: 0 0 20px; }
.edit-popup-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 20px 14px; border-bottom: 1px solid #f0f0f0;
}
.edit-popup-title { font-size: 16px; font-weight: 800; color: #1a1a2e; }

.ep-section-label {
  display: flex; align-items: center; gap: 8px;
  padding: 14px 20px 6px;
  font-size: 12px; font-weight: 700; color: #666;
  text-transform: uppercase; letter-spacing: 0.5px;
}
.ep-dot { width: 8px; height: 8px; border-radius: 50%; }
.ep-dot.blue { background: #2563eb; }
.ep-dot.red  { background: #e03131; }

.ep-field { padding: 6px 20px; }
.ep-field-label { font-size: 12px; font-weight: 600; color: #888; margin-bottom: 5px; }
.ep-input {
  width: 100%; height: 44px; padding: 0 14px;
  border: 1.5px solid #e5e7eb; border-radius: 10px;
  font-size: 14px; color: #1a1a2e; outline: none;
  transition: border-color 0.2s; box-sizing: border-box;
  background: #fafafa;
}
.ep-input:focus { border-color: #2563eb; background: #fff; }
.ep-input-wrap {
  display: flex; align-items: center;
  border: 1.5px solid #e5e7eb; border-radius: 10px;
  padding: 0 12px; background: #fafafa;
  transition: border-color 0.2s;
}
.ep-input-wrap:focus-within { border-color: #2563eb; background: #fff; }
.ep-input-wrap .ep-input { border: none; padding: 0; background: transparent; }
.ep-input-wrap .ep-input:focus { border-color: transparent; }

.ep-save-btn {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  width: calc(100% - 40px); margin: 20px 20px 0;
  height: 48px; background: linear-gradient(90deg, #2563eb, #4f46e5);
  color: #fff; border: none; border-radius: 12px;
  font-size: 15px; font-weight: 700; cursor: pointer;
  box-shadow: 0 4px 14px rgba(37,99,235,0.3);
  transition: opacity 0.15s;
}
.ep-save-btn:disabled { opacity: 0.7; cursor: not-allowed; }
.ep-save-btn:active:not(:disabled) { opacity: 0.88; }
</style>
