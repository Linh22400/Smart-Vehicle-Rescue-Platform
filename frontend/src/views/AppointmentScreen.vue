<template>
  <div class="appointment-container">
    <van-nav-bar title="Xác Nhận Đặt Lịch" left-text="Hủy" left-arrow @click-left="$router.go(-1)" />
    
    <van-cell-group inset title="Thông tin dịch vụ" class="mt-2">
      <van-cell title="Gara" :value="route.query.mechanicName" />
      <van-cell title="Dịch vụ" :value="route.query.serviceName" />
      <van-cell title="Giá dự kiến" :value="formatPrice(route.query.price)" />
    </van-cell-group>

    <van-form @submit="onSubmit">
      <van-cell-group inset title="Thời gian & Ghi chú" class="mt-2">
        <!-- HTML5 datetime-local input is simpler for MVP than custom Vant picker -->
        <van-field name="datetime" label="Thời gian">
            <template #input>
                <input type="datetime-local" v-model="apptTime" required style="width: 100%; border: none; background: transparent;" />
            </template>
        </van-field>
        
        <van-field
          v-model="note"
          name="note"
          rows="2"
          autosize
          label="Ghi chú"
          type="textarea"
          placeholder="Ví dụ: Xe vision đời 2020..."
        />
      </van-cell-group>

      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          Đặt Lịch Ngay
        </van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { showSuccessToast, showFailToast } from 'vant';

const route = useRoute();
const router = useRouter();

const apptTime = ref('');
const note = ref('');
const loading = ref(false);

const formatPrice = (p) => {
    return Number(p || 0).toLocaleString('vi-VN') + ' VNĐ';
};

const onSubmit = async () => {
    if (!apptTime.value) {
        showFailToast('Vui lòng chọn thời gian!');
        return;
    }

    const mechId = route.query.mechanicId;
    const servId = route.query.serviceId;

    if (!mechId || !servId) {
        showFailToast('Thiếu thông tin đặt lịch (ID). Vui lòng quay lại chọn lại.');
        return;
    }

    // Ensure date format is safe (append seconds if missing)
    const formattedTime = apptTime.value + ':00'; // Simple append, works for datetime-local input string check

    loading.value = true;
    try {
        await axios.post('/api/services/book/', {
            mechanic: mechId,
            service: servId,
            appointment_time: formattedTime,
            note: note.value
        });
        
        showSuccessToast('Đặt lịch thành công!');
        router.push('/history'); // Or maybe a dedicated Appointments list? For MVP use HistoryScreen if updated.
    } catch (error) {
        console.error(error);
        if (error.response && error.response.data) {
             showFailToast('Lỗi: ' + JSON.stringify(error.response.data));
        } else {
             showFailToast('Lỗi đặt lịch: ' + error.message);
        }
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.appointment-container {
    background: #f7f8fa;
    min-height: 100vh;
}
.mt-2 { margin-top: 15px; }
</style>
