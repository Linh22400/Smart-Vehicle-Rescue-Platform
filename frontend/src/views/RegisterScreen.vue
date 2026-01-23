<template>
  <div class="register-container">
    <h2 class="title">ĐĂNG KÝ</h2>
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
          Quay lại Đăng nhập
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
        is_mechanic: isMechanic.value
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
