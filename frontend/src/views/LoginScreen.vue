<template>
  <div class="login-container">
    <van-image
      width="150"
      height="150"
      src="https://img.freepik.com/free-vector/towing-car-concept-illustration_114360-1250.jpg"
      class="logo"
    />
    <h2 class="title">SMART RESCUE</h2>
    
    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="username"
          name="username"
          label="Tài khoản"
          placeholder="Nhập tài khoản"
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
      </van-cell-group>
      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          Đăng Nhập
        </van-button>
        <van-button round block type="default" class="mt-2" to="/register">
          Đăng Ký
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
const loading = ref(false);

const onSubmit = async (values) => {
  loading.value = true;
  try {
    const res = await axios.post('/api/users/login/', {
        username: values.username,
        password: values.password
    });
    
    // Save user info if needed
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
.login-container {
    padding-top: 50px;
    text-align: center;
    background-color: #f7f8fa;
    min-height: 100vh;
}
.title {
    color: #1989fa;
    margin-bottom: 30px;
}
.mt-2 { margin-top: 10px; }
</style>
