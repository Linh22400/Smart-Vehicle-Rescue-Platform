<template>
  <div class="login-page">
    <!-- Hero Section -->
    <div class="login-hero">
      <div class="hero-circles">
        <div class="circle c1"></div>
        <div class="circle c2"></div>
      </div>
      <van-image
        width="90"
        height="90"
        src="https://img.freepik.com/free-vector/towing-car-concept-illustration_114360-1250.jpg"
        round
        class="hero-logo"
      />
      <h1 class="hero-title">Smart Rescue</h1>
      <p class="hero-sub">Hệ thống cứu hộ xe thông minh</p>
    </div>

    <!-- Card -->
    <div class="login-card">
      <h2 class="card-title">Đăng nhập</h2>

      <van-form @submit="onSubmit">
        <!-- Username -->
        <div class="input-group">
          <span class="input-icon"><van-icon name="contact-o" /></span>
          <van-field
            v-model="username"
            name="username"
            placeholder="Tên tài khoản"
            class="custom-field"
            :border="false"
            :rules="[{ required: true, message: 'Vui lòng nhập tài khoản' }]"
          />
        </div>

        <!-- Password -->
        <div class="input-group">
          <span class="input-icon"><van-icon name="lock" /></span>
          <van-field
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            name="password"
            placeholder="Mật khẩu"
            class="custom-field"
            :border="false"
            :rules="[{ required: true, message: 'Vui lòng nhập mật khẩu' }]"
          />
          <span class="toggle-eye" @click="showPassword = !showPassword">
            <van-icon :name="showPassword ? 'eye-o' : 'closed-eye'" class="eye-icon" :class="{ rotated: showPassword }" />
          </span>
        </div>

        <!-- Login button -->
        <van-button
          round block
          type="primary"
          native-type="submit"
          :loading="loading"
          class="btn-login"
        >
          Đăng Nhập
        </van-button>
      </van-form>

      <div class="divider"><span>hoặc</span></div>

      <van-button round block plain class="btn-register" to="/register">
        Tạo tài khoản mới
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
const loading = ref(false);
const showPassword = ref(false);

const onSubmit = async (values) => {
  loading.value = true;
  try {
    const res = await axios.post('/api/users/login/', {
        username: values.username,
        password: values.password
    });
    localStorage.setItem('user', JSON.stringify(res.data.user));
    showSuccessToast('Đăng nhập thành công!');
    router.push('/booking');
  } catch (error) {
    showToast('Sai tài khoản hoặc mật khẩu');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

.login-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #4f46e5 0%, #dde7ff 55%, #f0f4ff 100%);
  font-family: 'Inter', sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
}

/* Hero */
.login-hero {
  width: 100%;
  position: relative;
  padding: 56px 0 80px;
  background: linear-gradient(145deg, #1a6fdf 0%, #2563eb 50%, #4f46e5 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: hidden;
  clip-path: ellipse(120% 100% at 50% 0%);
}

.hero-circles .circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
}
.c1 { width: 220px; height: 220px; background: #fff; top: -80px; right: -60px; }
.c2 { width: 140px; height: 140px; background: #fff; bottom: -40px; left: -30px; }

.hero-logo {
  border: 3px solid rgba(255,255,255,0.6);
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  margin-bottom: 14px;
}

.hero-title {
  color: #fff;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin: 0 0 4px;
}
.hero-sub {
  color: rgba(255,255,255,0.75);
  font-size: 13px;
  margin: 0;
}

/* Card */
.login-card {
  width: calc(100% - 32px);
  max-width: 420px;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 28px 22px 24px;
  margin-top: -36px;
  box-shadow: 0 8px 40px rgba(37,100,235,0.18);
  z-index: 1;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 22px;
  text-align: center;
}

/* Input groups */
.input-group {
  display: flex;
  align-items: center;
  background: #f5f7ff;
  border-radius: 12px;
  padding: 4px 12px;
  margin-bottom: 12px;
  border: 1.5px solid transparent;
  transition: border-color 0.2s;
}
.input-group:focus-within {
  border-color: #2563eb;
  background: #fff;
}
.input-icon {
  color: #2563eb;
  font-size: 18px;
  margin-right: 8px;
  flex-shrink: 0;
}
.custom-field {
  flex: 1;
  background: transparent !important;
  padding: 10px 0;
}
:deep(.custom-field .van-field__control) {
  font-size: 15px;
  color: #1a1a2e;
}
:deep(.custom-field .van-field__control::placeholder) {
  color: #bbb;
}

/* Buttons */
.btn-login {
  height: 48px;
  font-size: 15px;
  font-weight: 700;
  margin-top: 8px;
  background: linear-gradient(90deg, #2563eb, #4f46e5);
  border: none;
  box-shadow: 0 6px 16px rgba(37,100,235,0.35);
}

.divider {
  text-align: center;
  position: relative;
  margin: 18px 0 14px;
  color: #bbb;
  font-size: 12px;
}
.divider::before, .divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background: #eee;
}
.divider::before { left: 0; }
.divider::after { right: 0; }

/* Eye toggle */
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
  height: 44px;
  font-size: 14px;
  color: #2563eb;
  border-color: #2563eb;
  font-weight: 600;
}

</style>
