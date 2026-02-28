<template>
  <div class="terms-screen">
    <van-nav-bar
      title="Điều Khoản Dịch Vụ"
      left-arrow
      @click-left="onClickLeft"
    />
    <div class="p-4 content">
        <h3>1. Chấp nhận điều khoản</h3>
        <p>Bằng việc sử dụng ứng dụng Smart Rescue, bạn đồng ý tuân thủ các quy định và điều kiện sử dụng do chúng tôi đề ra.</p>

        <h3>2. Quyền và nghĩa vụ</h3>
        <p>Người dùng cam kết cung cấp thông tin chính xác khi đặt lịch hoặc gọi cứu hộ khẩn cấp.</p>

        <h3>3. Trách nhiệm của Thợ sửa xe</h3>
        <p>Thợ sửa xe trên nền tảng cam kết cung cấp dịch vụ trung thực, sửa chữa tận tình và báo giá rõ ràng trước khi tiến hành.</p>
        
        <h3>4. Miễn trừ trách nhiệm</h3>
        <p>Chúng tôi không chịu trách nhiệm cho các hư hỏng phát sinh ngoài phạm vi dịch vụ được thỏa thuận giữa hai bên trên nền tảng.</p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();
const onClickLeft = () => router.back();
</script>

<style scoped>
.terms-screen { min-height: 100vh; background: var(--van-background-2); color: var(--van-text-color); }
.p-4 { padding: 20px; }
.content h3 { font-size: 16px; margin-top: 20px; margin-bottom: 10px; }
.content p { font-size: 14px; line-height: 1.5; color: var(--van-text-color-2); }
</style>
