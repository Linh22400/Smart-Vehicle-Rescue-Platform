<template>
  <div class="privacy-screen">
    <van-nav-bar
      title="Chính Sách Bảo Mật"
      left-arrow
      @click-left="onClickLeft"
    />
    <div class="p-4 content">
        <h3>1. Thu thập thông tin</h3>
        <p>Chúng tôi chỉ thu thập các thông tin cơ bản: Tên, Số điện thoại và Vị trí (Tọa độ GPS) của bạn khi sử dụng tính năng gọi cứu hộ SOS.</p>

        <h3>2. Sử dụng thông tin</h3>
        <p>Vị trí của bạn được sử dụng duy nhất cho mục đích giúp thợ sửa xe tìm đường đến hỗ trợ. Chúng tôi không bán dữ liệu của bạn cho bên thứ ba.</p>

        <h3>3. Lưu trữ dữ liệu</h3>
        <p>Dữ liệu lịch sử đặt lịch và hóa đơn được mã hóa và lưu trữ an toàn trên máy chủ của hệ thống Smart Rescue.</p>
        
        <h3>4. Yêu cầu xóa dữ liệu</h3>
        <p>Bạn có quyền yêu cầu xóa toàn bộ lịch sử và tài khoản của mình bất kỳ lúc nào bằng cách liên hệ với bộ phận hỗ trợ.</p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();
const onClickLeft = () => router.back();
</script>

<style scoped>
.privacy-screen { min-height: 100vh; background: var(--van-background-2); color: var(--van-text-color); }
.p-4 { padding: 20px; }
.content h3 { font-size: 16px; margin-top: 20px; margin-bottom: 10px; }
.content p { font-size: 14px; line-height: 1.5; color: var(--van-text-color-2); }
</style>
