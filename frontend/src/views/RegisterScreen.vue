<template>
  <div class="register-container">
    <van-nav-bar title="Đăng Ký" left-arrow @click-left="$router.go(-1)" />
    <div class="logo-wrap">
      <van-image
        width="100"
        height="100"
        src="https://img.freepik.com/free-vector/towing-car-concept-illustration_114360-1250.jpg"
        class="logo"
      />
      <h2 class="title">TẠO TÀI KHOẢN</h2>
    </div>
    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="username"
          name="username"
          label="Tài khoản"
          placeholder="Chọn tên đăng nhập"
          :rules="[{ required: true, message: 'Vui lòng nhập tài khoản' }]"
        />
        <van-field
          v-model="password"
          type="password"
          name="password"
          label="Mật khẩu"
          placeholder="Nhập mật khẩu"
          :rules="[{ required: true, message: 'Vui lòng nhập mật khẩu' }]"
        />
        <van-field
          v-model="confirmPassword"
          type="password"
          name="confirmPassword"
          label="Nhập lại MK"
          placeholder="Xác nhận mật khẩu"
          :rules="[{ required: true, message: 'Vui lòng xác nhận mật khẩu' }]"
        />
        <van-field
          v-model="email"
          type="email"
          name="email"
          label="Email"
          placeholder="Nhập email (tùy chọn)"
          left-icon="envelop-o"
        />
        <van-field
          v-model="phoneNumber"
          type="tel"
          name="phone_number"
          label="Số ĐT"
          placeholder="Nhập số điện thoại"
          left-icon="phone-o"
        /> 
        <van-field name="isMechanic" label="Bạn là thợ?">
          <template #input>
            <van-switch v-model="isMechanic" />
          </template>
        </van-field>
      </van-cell-group>

      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          Đăng Ký
        </van-button>
        <van-button round block type="default" class="mt-2" to="/login">
          Đã có tài khoản? Đăng nhập
        </van-button>
      </div>
    </van-form>
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

const onSubmit = async (values) => {
  if (password.value !== confirmPassword.value) {
    showToast('Mật khẩu không khớp!');
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
.register-container {
    background-color: #f7f8fa;
    min-height: 100vh;
    padding-bottom: 40px;
}
.logo-wrap {
    padding-top: 20px;
    text-align: center;
}
.title {
    color: #1989fa;
    margin: 10px 0 20px 0;
    font-size: 20px;
}
.mt-2 { margin-top: 10px; }
</style>
