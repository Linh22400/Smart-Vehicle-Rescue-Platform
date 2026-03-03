<template>
  <div class="history-page">
    <div class="history-hero">
      <van-icon name="orders-o" size="22" color="#fff" />
      <span class="history-hero-title">Lịch Sử Hoạt Động</span>
    </div>

    <van-tabs v-model:active="activeTab" sticky :line-width="40">
      <van-tab title="SOS Cứu Hộ">
        <div v-if="loadingSOS" class="hst-loading">Đang tải...</div>
        <van-empty v-if="!loadingSOS && sosBookings.length === 0"
          image="/empty.png" description="Chưa có chuyến cứu hộ nào" class="hst-empty" />

        <div class="hst-list">
          <div v-for="item in sosBookings" :key="'sos-'+item.id" class="hst-card">
            <div class="hst-card-header">
              <div class="hst-icon-wrap sos"><van-icon name="phone-o" size="16" color="#fff" /></div>
              <div class="hst-meta">
                <div class="hst-title">Cứu hộ #{{ item.id }}</div>
                <div class="hst-date">{{ formatDate(item.created_at) }}</div>
              </div>
              <span class="hst-chip" :class="'chip-' + item.status.toLowerCase()">
                {{ translateStatus(item.status) }}
              </span>
            </div>
            <div class="hst-body">
              <div class="hst-row">
                <van-icon name="location-o" size="13" color="#888" />
                <span>{{ item.customer_lat?.toFixed(4) }}, {{ item.customer_lon?.toFixed(4) }}</span>
              </div>
              <div class="hst-row">
                <van-icon name="manager-o" size="13" color="#888" />
                <span>{{ item.mechanic_name || (item.mechanic ? 'Thợ #'+item.mechanic : 'Chưa có thợ') }}</span>
              </div>
              <div class="hst-row" v-if="item.problem_description">
                <van-icon name="warn-o" size="13" color="#888" />
                <span>{{ item.problem_description }}</span>
              </div>
            </div>
            <div class="hst-footer">
              <van-button v-if="item.status==='PENDING'" size="mini" type="danger" plain round @click="cancelBooking(item.id,'SOS')">Hủy</van-button>
              <van-button v-if="item.status==='COMPLETED' && item.mechanic && !item.has_sos_review"
                size="mini" type="primary" plain round @click="openSOSRating(item)">★ Đánh giá</van-button>
              <span v-if="item.status==='COMPLETED' && item.has_sos_review" class="rated-badge">✓ Đã đánh giá</span>
            </div>
          </div>
        </div>
      </van-tab>

      <van-tab title="Lịch Bảo Dưỡng">
        <div v-if="loadingAppt" class="hst-loading">Đang tải...</div>
        <van-empty v-if="!loadingAppt && appointments.length === 0"
          description="Chưa có lịch hẹn nào" class="hst-empty" />

        <div class="hst-list">
          <div v-for="appt in appointments" :key="'appt-'+appt.id" class="hst-card">
            <div class="hst-card-header">
              <div class="hst-icon-wrap appt"><van-icon name="shop-o" size="16" color="#fff" /></div>
              <div class="hst-meta">
                <div class="hst-title">{{ appt.service_details ? appt.service_details.name : 'Dịch vụ' }}</div>
                <div class="hst-date">{{ formatDate(appt.appointment_time) }}</div>
              </div>
              <span class="hst-chip" :class="'chip-' + appt.status.toLowerCase()">
                {{ translateStatus(appt.status) }}
              </span>
            </div>
            <div class="hst-body">
              <div class="hst-row">
                <van-icon name="manager-o" size="13" color="#888" />
                <span>{{ appt.mechanic_name || 'Chưa rõ' }}</span>
              </div>
              <div class="hst-row" v-if="appt.note">
                <van-icon name="notes-o" size="13" color="#888" />
                <span>{{ appt.note }}</span>
              </div>
            </div>
            <div class="hst-footer">
              <van-button v-if="appt.status==='PENDING'||appt.status==='CONFIRMED'"
                size="mini" type="danger" plain round @click="cancelBooking(appt.id,'APPT')">Hủy</van-button>
              <van-button v-if="appt.status==='COMPLETED' && !appt.has_review"
                size="mini" type="primary" plain round @click="openRating(appt)">★ Đánh giá</van-button>
              <span v-if="appt.status==='COMPLETED' && appt.has_review" class="rated-badge">✓ Đã đánh giá</span>
            </div>
          </div>
        </div>
      </van-tab>

      <!-- AI DIAGNOSIS HISTORY TAB -->
      <van-tab title="🤖 Chẩn đoán AI">
        <div v-if="loadingAI" class="text-center p-4">Đang tải...</div>
        <van-empty v-if="!loadingAI && aiReports.length === 0" description="Chưa có lịch sử chẩn đoán nào" />

        <!-- Cleanup button -->
        <div v-if="aiReports.length > 0" class="cleanup-bar">
          <span class="cleanup-info">{{ aiReports.length }} báo cáo</span>
          <van-button size="mini" plain type="warning" @click="cleanupOldReports">Xóa &gt; 30 ngày</van-button>
        </div>

        <div class="ai-history-list">
          <div v-for="r in aiReports" :key="r.id" class="ai-history-card">
            <!-- Header -->
            <div class="aih-header">
              <div class="aih-strip" :class="'aih-' + getSeverityKey(r.severity)"></div>
              <div class="aih-meta">
                <span class="aih-diagnosis">{{ r.diagnosis }}</span>
                <span class="aih-date">{{ formatDate(r.created_at) }}</span>
              </div>
              <van-tag :type="r.can_drive ? 'success' : 'danger'" size="mini" class="aih-drive">
                {{ r.can_drive ? 'Lái được' : 'Không lái' }}
              </van-tag>
            </div>
            <!-- Detail row -->
            <div class="aih-detail">{{ r.details }}</div>
            <div class="aih-footer">
              <span class="aih-price">💰 {{ r.estimated_price }}</span>
              <van-button size="mini" type="danger" plain @click="deleteAIReport(r.id)">Xóa</van-button>
            </div>
          </div>
        </div>
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

// AI History State
const aiReports = ref([]);
const loadingAI = ref(false);

const getSeverityKey = (s) => {
    const map = { 'Nhẹ':'low','Trung bình':'medium','Nghiêm trọng':'high','Nguy hiểm':'critical' };
    return map[s] || 'low';
};

const loadAIReports = async () => {
    loadingAI.value = true;
    try {
        const res = await axios.get('/api/ai/history/');
        aiReports.value = res.data;
    } catch(e) { console.error('AI history load error', e); }
    finally { loadingAI.value = false; }
};

const deleteAIReport = async (id) => {
    await showConfirmDialog({ title: 'Xóa báo cáo?', message: 'Hành động này không thể hoàn tác.' })
        .then(async () => {
            await axios.delete(`/api/ai/history/${id}/delete/`);
            aiReports.value = aiReports.value.filter(r => r.id !== id);
            showSuccessToast('Đã xóa báo cáo');
        }).catch(() => {});
};

const cleanupOldReports = async () => {
    await showConfirmDialog({
        title: 'Xóa báo cáo cũ?',
        message: 'Xóa tất cả báo cáo cũ hơn 30 ngày?'
    }).then(async () => {
        const res = await axios.delete('/api/ai/history/cleanup/?days=30');
        showSuccessToast(res.data.message);
        loadAIReports();
    }).catch(() => {});
};

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

    // Fetch AI Reports (non-blocking – runs in parallel)
    loadAIReports();

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
        const mechId = selectedAppt.value.mechanic;
        const payload = {
            mechanic:   mechId,
            rating:     ratingValue.value,
            comment:    ratingComment.value,
        };
        if (sosRatingMode.value) {
            payload.appointment   = null;
            payload.sos_booking_id = selectedAppt.value.id;   // link review to specific SOS booking
        } else {
            payload.appointment = selectedAppt.value.id;
        }
        await axios.post('/api/services/review/add/', payload);

        showSuccessToast('Cảm ơn bạn đã đánh giá!');
        showRating.value = false;

        // Refresh the relevant list from server so has_sos_review / has_review reflects truth
        if (sosRatingMode.value) {
            const res = await axios.get('/api/bookings/history/');
            sosBookings.value = res.data;
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
/* ─── Page ─── */
.history-page {
  min-height: 100vh;
  background: #f3f4f8;
  font-family: 'Inter', sans-serif;
  padding-bottom: 70px;
}

/* Hero */
.history-hero {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 18px;
  background: linear-gradient(135deg, #1a6fdf, #4f46e5);
}
.history-hero-title {
  color: #fff;
  font-size: 17px;
  font-weight: 700;
}

/* Tabs */
:deep(.van-tabs__wrap) { background: #fff; }

/* ─── History card ─── */
.hst-loading { text-align: center; padding: 28px 16px; color: #aaa; font-size: 14px; }
.hst-empty   { padding: 32px 0; }
.hst-list    { padding: 10px 12px 10px; }

.hst-card {
  background: #fff;
  border-radius: 14px;
  margin-bottom: 10px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.hst-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-bottom: 1px solid #f3f4f8;
}
.hst-icon-wrap {
  width: 38px; height: 38px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.hst-icon-wrap.sos  { background: linear-gradient(135deg, #e03131, #c92a2a); }
.hst-icon-wrap.appt { background: linear-gradient(135deg, #2563eb, #4f46e5); }

.hst-meta { flex: 1; min-width: 0; }
.hst-title { font-size: 14px; font-weight: 700; color: #1a1a2e; }
.hst-date  { font-size: 11px; color: #aaa; margin-top: 2px; }

/* Chips */
.hst-chip {
  font-size: 11px; font-weight: 700;
  padding: 3px 10px; border-radius: 20px;
  flex-shrink: 0;
}
.chip-pending   { background: #fff8e1; color: #b45309; }
.chip-accepted  { background: #e0eaff; color: #2563eb; }
.chip-confirmed { background: #e0eaff; color: #2563eb; }
.chip-completed { background: #d4fae4; color: #1a7a4a; }
.chip-cancelled { background: #f3f4f8; color: #aaa; }

/* Body rows */
.hst-body { padding: 8px 14px 4px; }
.hst-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

/* Footer */
.hst-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 8px 14px;
  border-top: 1px solid #f3f4f8;
  background: #fafafa;
}
.rated-badge {
  font-size: 11px;
  color: #1a7a4a;
  font-weight: 600;
  align-self: center;
}

/* ── AI History Tab ── */
.cleanup-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    background: #fff;
    border-bottom: 1px solid #f0f0f0;
}
.cleanup-info { font-size: 13px; color: #999; }

.ai-history-list { padding: 10px 12px 60px; }

.ai-history-card {
    background: #fff;
    border-radius: 14px;
    margin-bottom: 10px;
    overflow: hidden;
    box-shadow: 0 1px 5px rgba(0,0,0,0.07);
}
.aih-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 14px;
}
/* Severity left strip */
.aih-strip {
    width: 4px;
    height: 40px;
    border-radius: 4px;
    flex-shrink: 0;
}
.aih-low    { background: #1db954; }
.aih-medium { background: #f5a623; }
.aih-high   { background: #e03131; }
.aih-critical { background: #c0392b; }

.aih-meta { flex: 1; min-width: 0; }
.aih-diagnosis {
    display: block;
    font-size: 14px;
    font-weight: 600;
    color: #1a1a1a;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.aih-date { display: block; font-size: 11px; color: #bbb; margin-top: 2px; }
.aih-drive { flex-shrink: 0; }

.aih-detail {
    font-size: 12px;
    color: #666;
    line-height: 1.6;
    padding: 0 14px 10px;
    border-top: 1px solid #f5f5f5;
    padding-top: 8px;
}

.aih-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 14px;
    background: #fafafa;
    border-top: 1px solid #f0f0f0;
}
.aih-price { font-size: 13px; font-weight: 600; color: #2d6cdf; }

</style>
