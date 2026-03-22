<template>
  <div class="register-page">
    <!-- Khối ảnh nền nổi bật -->
    <div class="reg-hero">
      <div class="hero-circles">
        <div class="circle c1"></div>
        <div class="circle c2"></div>
      </div>
      <van-icon name="arrow-left" class="back-btn" size="20" color="#fff" @click="$router.go(-1)" />
      <van-image
        width="72"
        height="72"
        src="https://img.freepik.com/free-vector/towing-car-concept-illustration_114360-1250.jpg"
        round
        class="hero-logo"
      />
      <h1 class="hero-title">Tạo Tài Khoản</h1>
      <p class="hero-sub">Tham gia hệ thống cứu hộ thông minh</p>
    </div>

    <!-- Thẻ đăng ký -->
    <div class="reg-card">
      <van-form @submit="onSubmit">

        <div class="section-label">Thông tin đăng nhập</div>

        <div class="input-group">
          <span class="input-icon"><van-icon name="contact-o" /></span>
          <van-field v-model="username" name="username" placeholder="Tên tài khoản *"
            class="custom-field" :border="false"
            :rules="[{ required: true, message: 'Vui lòng nhập tài khoản' }]" />
        </div>

        <div class="input-group">
          <span class="input-icon"><van-icon name="lock" /></span>
          <van-field v-model="password" :type="showPassword ? 'text' : 'password'" name="password" placeholder="Mật khẩu *"
            class="custom-field" :border="false"
            :rules="[{ required: true, message: 'Vui lòng nhập mật khẩu' }]" />
          <span class="toggle-eye" @click="showPassword = !showPassword">
            <van-icon :name="showPassword ? 'eye-o' : 'closed-eye'" class="eye-icon" :class="{ rotated: showPassword }" />
          </span>
        </div>

        <div class="input-group">
          <span class="input-icon"><van-icon name="shield-o" /></span>
          <van-field v-model="confirmPassword" :type="showConfirm ? 'text' : 'password'" name="confirmPassword"
            placeholder="Xác nhận mật khẩu *" class="custom-field" :border="false"
            :rules="[{ required: true, message: 'Vui lòng xác nhận mật khẩu' }]" />
          <span class="toggle-eye" @click="showConfirm = !showConfirm">
            <van-icon :name="showConfirm ? 'eye-o' : 'closed-eye'" class="eye-icon" :class="{ rotated: showConfirm }" />
          </span>
        </div>

        <div class="section-label">Thông tin liên hệ <span class="opt">— không bắt buộc</span></div>

        <div class="input-group">
          <span class="input-icon"><van-icon name="envelop-o" /></span>
          <van-field v-model="email" type="email" name="email" placeholder="Email"
            class="custom-field" :border="false" />
        </div>

        <div class="input-group">
          <span class="input-icon"><van-icon name="phone-o" /></span>
          <van-field v-model="phoneNumber" type="tel" name="phone_number" placeholder="Số điện thoại"
            class="custom-field" :border="false" />
        </div>

        <!-- Nút bật tắt chọn Thợ -->
        <div class="mechanic-row">
          <div>
            <div class="mech-label">Đăng ký là Thợ Cứu Hộ</div>
            <div class="mech-sub">Bật nếu bạn muốn nhận đơn cứu hộ</div>
          </div>
          <van-switch v-model="isMechanic" size="22px" />
        </div>

        <van-button round block type="primary" native-type="submit"
          :loading="loading" class="btn-register">
          Tạo Tài Khoản
        </van-button>
      </van-form>

      <div class="divider"><span>đã có tài khoản?</span></div>
      <van-button round block plain class="btn-login" to="/login">
        Đăng nhập ngay
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { showToast, showSuccessToast } from 'vant';

const router = useRouter();
const username = ref('');
const password = ref('');
const confirmPassword = ref('');
const email = ref('');
const phoneNumber = ref('');
const isMechanic = ref(false);
const loading = ref(false);
const showPassword = ref(false);
const showConfirm = ref(false);

const onSubmit = async (values) => {
  if (password.value !== confirmPassword.value) {
    showToast('Mật khẩu không khớp!');
    return;
  }
  if (password.value.length < 6) {
    showToast('Mật khẩu phải có ít nhất 6 ký tự!');
    return;
  }
  loading.value = true;
  try {
    await axios.post('/api/users/register/', {
        username: values.username,
        password: values.password,
        is_mechanic: isMechanic.value,
        email: email.value || '',
        phone_number: phoneNumber.value || ''
    });
    showSuccessToast('Đăng ký thành công! Vui lòng đăng nhập.');
    router.push('/login');
  } catch (error) {
    showToast('Lỗi đăng ký (Tên có thể đã tồn tại)');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

.register-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #4f46e5 0%, #dde7ff 55%, #f0f4ff 100%);
  font-family: 'Inter', sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
}

/* ─── Ảnh Bìa Nổi Bật ─── */
.reg-hero {
  width: 100%;
  position: relative;
  padding: 40px 0 70px;
  background: linear-gradient(145deg, #1a6fdf 0%, #2563eb 50%, #4f46e5 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
  clip-path: ellipse(120% 100% at 50% 0%);
}
.back-btn {
  position: absolute;
  top: 16px;
  left: 16px;
  cursor: pointer;
  z-index: 2;
}
.hero-circles .circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
}
.c1 { width: 200px; height: 200px; background: #fff; top: -70px; right: -50px; }
.c2 { width: 120px; height: 120px; background: #fff; bottom: -30px; left: -20px; }

.hero-logo {
  border: 3px solid rgba(255,255,255,0.6);
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  margin-bottom: 12px;
}
.hero-title  { color: #fff; font-size: 22px; font-weight: 700; margin: 0 0 4px; }
.hero-sub    { color: rgba(255,255,255,0.75); font-size: 12px; margin: 0; }

/* ─── Thẻ Thông Tin Đăng Ký ─── */
.reg-card {
  width: calc(100% - 32px);
  max-width: 420px;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 24px 20px 20px;
  margin-top: -36px;
  box-shadow: 0 8px 40px rgba(37,100,235,0.18);
  z-index: 1;
  margin-bottom: 32px;
}

/* Tiêu đề phân mục */
.section-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #aaa;
  margin: 16px 0 8px;
}
.section-label:first-of-type { margin-top: 0; }
.opt { font-weight: 400; text-transform: none; letter-spacing: 0; }

/* Nhóm ô nhập liệu */
.input-group {
  display: flex;
  align-items: center;
  background: #f5f7ff;
  border-radius: 12px;
  padding: 4px 12px;
  margin-bottom: 10px;
  border: 1.5px solid transparent;
  transition: border-color 0.2s;
}
.input-group:focus-within {
  border-color: #2563eb;
  background: #fff;
}
.input-icon {
  color: #2563eb;
  font-size: 17px;
  margin-right: 8px;
  flex-shrink: 0;
}
.custom-field { flex: 1; background: transparent !important; padding: 9px 0; }
:deep(.custom-field .van-field__control) { font-size: 14px; color: #1a1a2e; }
:deep(.custom-field .van-field__control::placeholder) { color: #bbb; }

/* Nút chuyển đổi (Đăng ký làm thợ) */
.mechanic-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f5f7ff;
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 16px;
}
.mech-label { font-size: 14px; font-weight: 600; color: #1a1a2e; }
.mech-sub   { font-size: 11px; color: #999; margin-top: 2px; }

/* Nút bật tắt ẩn/hiển thị mật khẩu */
.toggle-eye {
  padding: 0 4px;
  cursor: pointer;
  color: #aaa;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}
.toggle-eye:hover { color: #2563eb; }
.eye-icon {
  font-size: 18px;
  transition: transform 0.3s ease, opacity 0.2s;
}
.eye-icon.rotated { transform: rotate(180deg); opacity: 0.7; }

.btn-register {
  height: 48px;
  font-size: 15px;
  font-weight: 700;
  background: linear-gradient(90deg, #2563eb, #4f46e5);
  border: none;
  box-shadow: 0 6px 16px rgba(37,100,235,0.35);
}

.divider {
  text-align: center;
  position: relative;
  margin: 16px 0 12px;
  color: #bbb;
  font-size: 12px;
}
.divider::before, .divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 35%;
  height: 1px;
  background: #eee;
}
.divider::before { left: 0; }
.divider::after { right: 0; }

.btn-login {
  height: 42px;
  font-size: 14px;
  color: #2563eb;
  border-color: #2563eb;
  font-weight: 600;
}
</style>
