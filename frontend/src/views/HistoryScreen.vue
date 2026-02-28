<template>
  <div class="history-container">
    <van-nav-bar title="Lịch Sử Hoạt Động" />
    
    <van-tabs v-model:active="activeTab" sticky>
      <van-tab title="SOS Cứu Hộ">
        <div v-if="loadingSOS" class="text-center p-4">Đang tải...</div>
        <van-empty v-if="!loadingSOS && sosBookings.length === 0" description="Chưa có chuyến cứu hộ nào" />
        
        <van-cell-group inset class="mt-2" v-for="item in sosBookings" :key="'sos-'+item.id">
          <van-cell :title="'Cứu hộ #' + item.id" :label="formatDate(item.created_at)" center>
            <template #right-icon>
                <van-tag :type="getStatusColor(item.status)">{{ translateStatus(item.status) }}</van-tag>
            </template>
          </van-cell>
          <van-cell title="Vị trí" :label="`${item.customer_lat}, ${item.customer_lon}`" />
          <van-cell title="Thợ phụ trách" :value="item.mechanic_name || (item.mechanic ? '#' + item.mechanic : 'Chưa có')" />
          <van-cell title="Vấn đề" :label="item.problem_description || 'Không có'" />
          
          <!-- Hủy Cứu Hộ - chỉ khi chưa có thợ -->
          <div class="text-right p-2">
             <van-button v-if="item.status === 'PENDING'" size="small" type="danger" plain @click="cancelBooking(item.id, 'SOS')" class="mr-2">Hủy Cứu Hộ</van-button>
             <van-button v-if="item.status === 'COMPLETED' && item.mechanic && !item.has_sos_review" size="small" type="primary" plain @click="openSOSRating(item)">Đánh giá Thợ</van-button>
             <span v-if="item.status === 'COMPLETED' && item.has_sos_review" style="font-size:12px; color: #07c160">✓ Đã đánh giá</span>
          </div>
        </van-cell-group>
      </van-tab>

      <van-tab title="Lịch Bảo Dưỡng">
        <div v-if="loadingAppt" class="text-center p-4">Đang tải...</div>
        <van-empty v-if="!loadingAppt && appointments.length === 0" description="Chưa có lịch hẹn nào" />

        <van-cell-group inset class="mt-2" v-for="appt in appointments" :key="'appt-'+appt.id">
          <van-cell :title="appt.service_details ? appt.service_details.name : 'Dịch vụ'" :label="formatDate(appt.appointment_time)" center>
            <template #right-icon>
                <van-tag :type="getStatusColor(appt.status)">{{ translateStatus(appt.status) }}</van-tag>
            </template>
          </van-cell>
          <van-cell title="Thợ/Gara" :value="appt.mechanic_name" />
          <van-cell title="Ghi chú" :label="appt.note" />
          
          <!-- Action Buttons -->
          <div class="text-right p-2">
             <van-button v-if="appt.status === 'PENDING' || appt.status === 'CONFIRMED'" size="small" type="danger" plain @click="cancelBooking(appt.id, 'APPT')" class="mr-2">Hủy Lịch</van-button>
             <van-button v-if="appt.status === 'COMPLETED' && !appt.has_review" size="small" type="primary" plain @click="openRating(appt)">Đánh giá</van-button>
             <span v-if="appt.status === 'COMPLETED' && appt.has_review" class="text-gray-500 text-sm">Đã đánh giá</span>
          </div>
        </van-cell-group>
      </van-tab>
    </van-tabs>

    <!-- RATING DIALOG - shared for both SOS and Appointment -->
    <van-dialog v-model:show="showRating" title="Đánh giá Thợ" show-cancel-button @confirm="submitRating">
        <div class="rating-content">
            <p>Vui lòng đánh giá dịch vụ:</p>
            <van-rate v-model="ratingValue" :size="30" color="#ffd21e" void-icon="star" void-color="#eee" />
            <van-field
                v-model="ratingComment"
                rows="2"
                autosize
                label="Nhận xét"
                type="textarea"
                placeholder="Nhập nhận xét của bạn..."
                class="mt-2"
                style="border: 1px solid #eee; border-radius: 4px;"
            />
        </div>
    </van-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const activeTab = ref(0);
const sosBookings = ref([]);
const appointments = ref([]);
const loadingSOS = ref(true);
const loadingAppt = ref(true);

// Rating State
const showRating = ref(false);
const ratingValue = ref(5);
const ratingComment = ref('');
const selectedAppt = ref(null);
const sosRatingMode = ref(false); // true = rating SOS, false = rating Appointment

onMounted(async () => {
    // Fetch SOS
    try {
        const res = await axios.get('/api/bookings/history/');
        sosBookings.value = res.data;
    } catch (e) {
        console.error("SOS load error", e);
    } finally {
        loadingSOS.value = false;
    }

    // Fetch Appointments
    try {
        const res = await axios.get('/api/services/history/');
        appointments.value = res.data;
    } catch (e) {
        console.error("Appt load error", e);
    } finally {
        loadingAppt.value = false;
    }
});

const getStatusColor = (status) => {
    switch(status) {
        case 'COMPLETED': return 'success';
        case 'ACCEPTED': 
        case 'CONFIRMED': return 'primary';
        case 'PENDING': return 'warning';
        case 'CANCELLED': return 'danger';
        default: return 'default';
    }
}

const translateStatus = (status) => {
    switch(status) {
        case 'PENDING': return 'Chờ xác nhận';
        case 'ACCEPTED': return 'Đang thực hiện';
        case 'CONFIRMED': return 'Đã xác nhận';
        case 'COMPLETED': return 'Hoàn thành';
        case 'CANCELLED': return 'Đã hủy';
        default: return status;
    }
}

const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleString('vi-VN');
}

const openRating = (appt) => {
    selectedAppt.value = appt;
    sosRatingMode.value = false;
    ratingValue.value = 5;
    ratingComment.value = '';
    showRating.value = true;
}

const openSOSRating = (sos) => {
    selectedAppt.value = sos;
    sosRatingMode.value = true;
    ratingValue.value = 5;
    ratingComment.value = '';
    showRating.value = true;
}

const submitRating = async () => {
    if (!selectedAppt.value) return;
    try {
        const mechId = sosRatingMode.value
            ? selectedAppt.value.mechanic // for SOS, mechanic is a user ID
            : selectedAppt.value.mechanic; // for Appt, mechanic is a MechanicProfile ID            
        
        await axios.post('/api/services/review/add/', {
            mechanic: mechId,
            appointment: sosRatingMode.value ? null : selectedAppt.value.id,
            rating: ratingValue.value,
            comment: ratingComment.value
        });
        showSuccessToast('Cảm ơn bạn đã đánh giá!');
        showRating.value = false;
        if (sosRatingMode.value) {
            sosBookings.value = sosBookings.value.map(b =>
                b.id === selectedAppt.value.id ? { ...b, has_sos_review: true } : b
            );
        } else {
            const res = await axios.get('/api/services/history/');
            appointments.value = res.data;
        }
    } catch (e) {
        if (e.response && e.response.data && e.response.data.error) {
            showFailToast('Lỗi: ' + e.response.data.error);
        } else {
            showFailToast('Lỗi gửi đánh giá');
        }
    }
}

import { showConfirmDialog, showToast, showSuccessToast, showFailToast } from 'vant';

const cancelBooking = (id, type) => {
    showConfirmDialog({
        title: 'Xác nhận hủy',
        message: 'Bạn có chắc chắn muốn hủy yêu cầu này?',
    }).then(async () => {
        try {
            if (type === 'SOS') {
                await axios.post(`/api/bookings/${id}/update-status/`, { status: 'CANCELLED' });
                // Refresh SOS list
                const res = await axios.get('/api/bookings/history/');
                sosBookings.value = res.data;
            } else {
                await axios.post(`/api/services/${id}/update-status/`, { status: 'CANCELLED' });
                // Refresh Appt list
                const resAppt = await axios.get('/api/services/history/');
                appointments.value = resAppt.data;
            }
            showToast('Đã hủy thành công');
        } catch (e) {
            showToast('Lỗi khi hủy');
            console.error(e);
        }
    }).catch(() => {
        // on cancel
    });
}
</script>

<style scoped>
.rating-content { padding: 20px; text-align: center; }
.text-right { text-align: right; }
.mr-2 { margin-right: 10px; }
.history-container {
    background: #f7f8fa;
    min-height: 100vh;
    padding-bottom: 60px;
}
.mt-2 { margin-top: 10px; margin-bottom: 10px; }
.text-center { text-align: center; }
.p-4 { padding: 20px; }
</style>
