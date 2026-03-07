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
        <!-- Search & Filter -->
        <div class="filter-bar">
          <van-field v-model="searchSOS" placeholder="Tìm kiếm..." clearable left-icon="search" size="small" />
          <div class="filter-pills">
            <span class="pill" :class="{active: filterSOS === ''}" @click="filterSOS = ''">Tất cả</span>
            <span class="pill" :class="{active: filterSOS === 'PENDING'}" @click="filterSOS = 'PENDING'">Chờ</span>
            <span class="pill" :class="{active: filterSOS === 'ON_THE_WAY'}" @click="filterSOS = 'ON_THE_WAY'">Đang đến</span>
            <span class="pill" :class="{active: filterSOS === 'COMPLETED'}" @click="filterSOS = 'COMPLETED'">Hoàn thành</span>
            <span class="pill" :class="{active: filterSOS === 'CANCELLED'}" @click="filterSOS = 'CANCELLED'">Hủy</span>
          </div>
        </div>

        <div class="hst-list">
          <div v-for="item in filteredSOS" :key="'sos-'+item.id" class="hst-card">
            <div class="hst-card-header" @click="openDetail(item)">
              <div class="hst-icon-wrap sos"><van-icon name="phone-o" size="16" color="#fff" /></div>
              <div class="hst-meta">
                <div class="hst-title">Cứu hộ {{ formatOrderId(item.id, 'SOS') }}</div>
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
              <van-button v-if="['ACCEPTED','ON_THE_WAY'].includes(item.status)" 
                size="mini" type="primary" round @click="openTracking(item)">
                <span style="display:flex;align-items:center;gap:4px"><van-icon name="location-o" /> Theo dõi Thợ</span>
              </van-button>
              <van-button v-if="item.status==='IN_PROGRESS'" size="mini" type="warning" plain round disabled>
                <span style="display:flex;align-items:center;gap:4px"><van-icon name="setting-o" /> Đang sửa</span>
              </van-button>
              <!-- Chat button for active SOS -->
              <van-button v-if="['ACCEPTED','ON_THE_WAY','IN_PROGRESS'].includes(item.status)" 
                size="mini" type="primary" plain round icon="chat-o" @click="openChat(item)" style="margin-left:4px">Chat</van-button>
              <!-- Payment button -->
              <van-button v-if="item.status==='COMPLETED' && item.payment_status==='UNPAID'" 
                size="mini" type="success" round @click="openPayment(item)">
                <span style="display:flex;align-items:center;gap:4px">Thanh toán {{ formatCost(item.repair_cost) }}</span>
              </van-button>
              <span v-if="item.status==='COMPLETED' && item.payment_status==='PAID'" class="paid-badge">
                <van-icon name="passed" /> Đã thanh toán {{ translatePaymentMethod(item.payment_method) }}
              </span>
              <span v-if="item.status==='COMPLETED' && item.payment_status==='PENDING'" class="pending-badge" style="color:#d48806; background:#fffbe6; padding:4px 8px; border-radius:4px; font-size:12px; border:1px solid #ffe58f; margin-left: 4px;">
                <van-icon name="clock-o" /> Đang chờ Thợ chốt
              </span>
              <van-button v-if="item.status==='COMPLETED' && item.mechanic && !item.has_sos_review"
                size="mini" type="primary" plain round @click="openSOSRating(item)">
                <span style="display:flex;align-items:center;gap:4px"><van-icon name="star-o" /> Đánh giá</span>
              </van-button>
              <span v-if="item.status==='COMPLETED' && item.has_sos_review" class="rated-badge">
                <van-icon name="success" /> Đã đánh giá
              </span>
            </div>
          </div>
        </div>
      </van-tab>

      <van-tab title="Lịch Bảo Dưỡng">
        <div v-if="loadingAppt" class="hst-loading">Đang tải...</div>
        <van-empty v-if="!loadingAppt && appointments.length === 0"
          description="Chưa có lịch hẹn nào" class="hst-empty" />

        <!-- Search & Filter -->
        <div class="filter-bar">
          <van-field v-model="searchAppt" placeholder="Tìm kiếm..." clearable left-icon="search" size="small" />
          <div class="filter-pills">
            <span class="pill" :class="{active: filterAppt === ''}" @click="filterAppt = ''">Tất cả</span>
            <span class="pill" :class="{active: filterAppt === 'PENDING'}" @click="filterAppt = 'PENDING'">Chờ</span>
            <span class="pill" :class="{active: filterAppt === 'CONFIRMED'}" @click="filterAppt = 'CONFIRMED'">Xác nhận</span>
            <span class="pill" :class="{active: filterAppt === 'COMPLETED'}" @click="filterAppt = 'COMPLETED'">Xong</span>
            <span class="pill" :class="{active: filterAppt === 'CANCELLED'}" @click="filterAppt = 'CANCELLED'">Hủy</span>
          </div>
        </div>

        <div class="hst-list">
          <div v-for="appt in filteredAppt" :key="'appt-'+appt.id" class="hst-card">
            <div class="hst-card-header" @click="openDetail(appt)">
              <div class="hst-icon-wrap appt"><van-icon name="shop-o" size="16" color="#fff" /></div>
              <div class="hst-meta">
                <div class="hst-title">{{ formatOrderId(appt.id, 'BD') }} - {{ appt.service_details ? appt.service_details.name : 'Dịch vụ' }}</div>
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
              <!-- Appointment Payment -->
              <van-button v-if="appt.status==='COMPLETED' && appt.payment_status==='UNPAID' && appt.service_details"
                size="mini" type="success" round @click="openApptPayment(appt)">
                <span style="display:flex;align-items:center;gap:4px">Thanh toán {{ formatCost(appt.service_details.price) }}</span>
              </van-button>
              <span v-if="appt.status==='COMPLETED' && appt.payment_status==='PAID'" class="paid-badge">
                <van-icon name="passed" /> Đã thanh toán {{ translatePaymentMethod(appt.payment_method) }}
              </span>
              <span v-if="appt.status==='COMPLETED' && appt.payment_status==='PENDING'" class="pending-badge" style="color:#d48806; background:#fffbe6; padding:4px 8px; border-radius:4px; font-size:12px; border:1px solid #ffe58f; margin-left: 4px;">
                <van-icon name="clock-o" /> Đang chờ Thợ chốt
              </span>
              <van-button v-if="appt.status==='COMPLETED' && !appt.has_review"
                size="mini" type="primary" plain round @click="openRating(appt)">
                <span style="display:flex;align-items:center;gap:4px"><van-icon name="star-o" /> Đánh giá</span>
              </van-button>
              <span v-if="appt.status==='COMPLETED' && appt.has_review" class="rated-badge">
                <van-icon name="success" /> Đã đánh giá
              </span>
            </div>
          </div>
        </div>
      </van-tab>

      <!-- AI DIAGNOSIS HISTORY TAB -->
      <van-tab>
        <template #title><Bot :size="15" style="vertical-align:-2px;margin-right:4px" /> Chẩn đoán AI</template>
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
                <span class="aih-diagnosis">
                  <Mic v-if="r.source === 'sound'" :size="15" color="#5c6bc0" style="margin-right:4px; vertical-align:-2px" />
                  <Camera v-else :size="15" color="#5c6bc0" style="margin-right:4px; vertical-align:-2px" />
                  {{ r.diagnosis }}
                </span>
                <span class="aih-date">{{ formatDate(r.created_at) }}</span>
              </div>
              <!-- Modernized Drive Badge -->
              <span class="aih-badge" :class="r.can_drive ? 'badge-safe' : 'badge-danger'">
                {{ r.can_drive ? 'Lái được' : 'Không lái' }}
              </span>
            </div>
            <!-- Detail row -->
            <div class="aih-detail">{{ r.details }}</div>
            <div class="aih-footer">
              <span class="aih-price">{{ r.estimated_price ? `${parseInt(r.estimated_price.replace(/,/g, '')).toLocaleString('vi-VN')} VNĐ` : '' }}</span>
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

    <!-- TRACKING POPUP (Grab-style) -->
    <van-popup v-model:show="showTracking" position="bottom" :style="{ height: '85%' }" round @opened="initTrackingMap" @closed="stopTrackingPolling">
      <div class="tracking-header">
        <div class="tracking-title">
          <span class="tracking-dot" :class="trackingStatus"></span>
          <span>{{ trackingStatusText }}</span>
        </div>
        <van-icon name="cross" size="20" color="#666" @click="showTracking = false" />
      </div>
      <div id="tracking-map" class="tracking-map"></div>
      <div class="tracking-info">
        <div class="tracking-mechanic">
          <van-icon name="manager-o" size="18" color="#2563eb" />
          <span>{{ trackingMechanicName }}</span>
        </div>
        <div class="tracking-badge">
          <van-tag :type="trackingStatus === 'on_the_way' ? 'primary' : trackingStatus === 'in_progress' ? 'success' : 'warning'" size="medium">
            {{ trackingStatusText }}
          </van-tag>
        </div>
      </div>
    </van-popup>

    <!-- PAYMENT POPUP -->
    <van-popup v-model:show="showPayment" position="bottom" :style="{ height: '45%' }" round>
      <div class="payment-container">
        <h3 class="payment-title" style="display:flex;align-items:center;justify-content:center;gap:6px">
          <van-icon name="balance-pay" color="#e74c3c" /> Thanh toán {{ paymentType === 'SOS' ? 'Sửa chữa' : 'Dịch vụ' }}
        </h3>
        <div class="payment-amount">
          {{ paymentType === 'SOS' ? formatCost(paymentItem?.repair_cost) : formatCost(paymentItem?.service_details?.price) }}
        </div>
        <p class="payment-subtitle">Chọn hình thức thanh toán:</p>
        <div class="payment-methods">
          <div class="payment-method-card" :class="{ active: selectedPaymentMethod === 'CASH' }" @click="selectedPaymentMethod = 'CASH'">
            <span class="pm-icon"><van-icon name="cash-back-record" /></span>
            <span class="pm-label">Tiền mặt</span>
          </div>
          <div class="payment-method-card" :class="{ active: selectedPaymentMethod === 'TRANSFER' }" @click="selectedPaymentMethod = 'TRANSFER'">
            <span class="pm-icon"><van-icon name="exchange" /></span>
            <span class="pm-label">Chuyển khoản</span>
          </div>
        </div>
        <van-button type="success" block round size="large" :disabled="!selectedPaymentMethod" @click="confirmPayment">
          Xác nhận Thanh toán
        </van-button>
      </div>
    </van-popup>

    <!-- VIETQR POPUP -->
    <van-popup v-model:show="showQR" position="center" :style="{ width: '85%', maxWidth: '400px', borderRadius: '12px', padding: '20px' }">
      <div v-if="qrUrl" style="text-align: center;">
        <h3 style="margin-top:0; font-size:18px; color: #1989fa;">Quét mã VietQR</h3>
        <p style="font-size:13px; color:#666; margin-bottom:15px">Sử dụng ứng dụng Ngân hàng để quét và thanh toán cho Thợ.</p>
        
        <van-image :src="qrUrl" width="100%" fit="contain" style="border:1px solid #eee; border-radius:8px; padding:10px; max-height: 45vh; margin: 0 auto; display: block;" />
        
        <div style="margin-top: 20px;">
           <van-button type="success" block round :loading="paymentProcessing" @click="processPaymentAPI('TRANSFER')">
             Xác nhận đã chuyển khoản
           </van-button>
           <van-button type="default" block round style="margin-top: 10px;" @click="showQR = false" :disabled="paymentProcessing">
             Quay lại
           </van-button>
        </div>
      </div>
    </van-popup>

    <!-- CANCEL REASON DIALOG -->
    <van-dialog v-model:show="showCancelDialog" title="Lý do hủy đơn" show-cancel-button
      confirm-button-text="Xác nhận hủy" cancel-button-text="Quay lại" @confirm="confirmCancel">
      <div style="padding: 16px;">
        <van-field v-model="cancelReasonInput" type="textarea" rows="3"
          placeholder="Nhập lý do hủy (bắt buộc)..." maxlength="200" show-word-limit />
      </div>
    </van-dialog>

    <!-- ORDER DETAIL POPUP -->
    <van-popup v-model:show="showOrderDetail" position="bottom" :style="{ height: '70%' }" round>
      <div v-if="detailItem" class="detail-container">
        <div class="detail-header">
          <h3 class="detail-title">Chi tiết đơn #{{ detailItem.id }}</h3>
          <van-icon name="cross" size="18" color="#888" @click="showOrderDetail = false" />
        </div>
        <div class="detail-body">
          <div class="detail-row">
            <span class="detail-label">Trạng thái</span>
            <van-tag :type="detailTagType" size="medium">{{ translateStatus(detailItem.status) }}</van-tag>
          </div>
          <div class="detail-row">
            <span class="detail-label">Loại đơn</span>
            <span class="detail-value">{{ detailItem.vehicle_type ? 'SOS Cứu hộ' : 'Lịch bảo dưỡng' }}</span>
          </div>
          <div v-if="detailItem.damage_image" class="detail-row">
            <span class="detail-label">Ảnh đính kèm</span>
            <div style="flex: 2; text-align: right;">
              <van-image width="80" height="80" radius="8" :src="detailItem.damage_image" fit="cover" />
            </div>
          </div>
          <div class="detail-row">
            <span class="detail-label">Thợ sửa</span>
            <span class="detail-value">{{ detailItem.mechanic_name || 'N/A' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Ngày tạo</span>
            <span class="detail-value">{{ formatDate(detailItem.created_at || detailItem.appointment_time) }}</span>
          </div>
          <div v-if="detailItem.problem_description" class="detail-row">
            <span class="detail-label">Mô tả</span>
            <span class="detail-value">{{ detailItem.problem_description }}</span>
          </div>
          <div v-if="detailItem.note" class="detail-row">
            <span class="detail-label">Ghi chú</span>
            <span class="detail-value">{{ detailItem.note }}</span>
          </div>
          <div v-if="detailItem.service_details" class="detail-row">
            <span class="detail-label">Dịch vụ</span>
            <span class="detail-value">{{ detailItem.service_details.name }} — {{ formatCost(detailItem.service_details.price) }}</span>
          </div>
          <div v-if="detailItem.repair_cost" class="detail-row highlight">
            <span class="detail-label">Chi phí sửa</span>
            <span class="detail-value cost">{{ formatCost(detailItem.repair_cost) }}</span>
          </div>
          <div v-if="detailItem.payment_status" class="detail-row">
            <span class="detail-label">Thanh toán</span>
            <span class="detail-value" style="display:flex;align-items:center;gap:4px;justify-content:flex-end">
              <van-icon :name="detailItem.payment_status === 'PAID' ? 'passed' : 'clock-o'" :color="detailItem.payment_status === 'PAID' ? '#07c160' : '#f5a623'" />
              {{ detailItem.payment_status === 'PAID' ? 'Đã thanh toán ' + translatePaymentMethod(detailItem.payment_method) : 'Chưa thanh toán' }}
            </span>
          </div>
          <div v-if="detailItem.cancel_reason" class="detail-row cancel">
            <span class="detail-label" style="display:flex;align-items:center;gap:4px"><van-icon name="close" color="#ee0a24" /> Lý do hủy</span>
            <span class="detail-value">{{ detailItem.cancel_reason }}</span>
          </div>
        </div>
      </div>
    </van-popup>

    <!-- CHAT POPUP -->
    <van-popup v-model:show="showChat" position="bottom" :style="{ height: '80%', display: 'flex', flexDirection: 'column' }" round>
      <div class="chat-header">
        <h3 style="margin:0; font-size:16px; display:flex; align-items:center; gap:6px;">
          <van-icon name="chat-o" size="18" /> Chat với Thợ
        </h3>
        <van-icon name="cross" size="18" @click="closeChat" />
      </div>
      <div class="chat-body" id="chat-body-scroller">
        <div v-if="loadingChat" class="text-center p-4">Đang tải...</div>
        <div v-for="msg in chatMessages" :key="msg.id" class="chat-msg" :class="msg.is_mechanic ? 'msg-them' : 'msg-me'">
          <div class="msg-bubble">
            <div class="msg-text">{{ msg.text }}</div>
            <div class="msg-time">{{ new Date(msg.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</div>
          </div>
        </div>
      </div>
      <div class="chat-footer">
        <van-field v-model="newChatMessage" placeholder="Nhập tin nhắn..." clearable @keyup.enter="sendChat" />
        <van-button type="primary" icon="guide-o" round style="margin-left: 8px; width:40px; height:40px; padding:0;" @click="sendChat"></van-button>
      </div>
    </van-popup>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import axios from 'axios';
import { Camera, Mic, Bot } from 'lucide-vue-next';
import L from 'leaflet';
import 'leaflet-routing-machine';
import 'leaflet-routing-machine/dist/leaflet-routing-machine.css';

const activeTab = ref(0);
const sosBookings = ref([]);
const appointments = ref([]);
const loadingSOS = ref(true);
const loadingAppt = ref(true);

// Search & Filter
const searchSOS = ref('');
const filterSOS = ref('');
const searchAppt = ref('');
const filterAppt = ref('');

const formatOrderId = (id, prefix) => {
    return `${prefix}-${String(id).padStart(5, '0')}`;
};

const filteredSOS = computed(() => {
    let list = sosBookings.value;
    if (filterSOS.value) list = list.filter(b => b.status === filterSOS.value);
    if (searchSOS.value.trim()) {
        const q = searchSOS.value.toLowerCase();
        list = list.filter(b => 
            String(b.id).includes(q) || 
            (b.mechanic_name || '').toLowerCase().includes(q) ||
            (b.problem_description || '').toLowerCase().includes(q)
        );
    }
    return list;
});

const filteredAppt = computed(() => {
    let list = appointments.value;
    if (filterAppt.value) list = list.filter(a => a.status === filterAppt.value);
    if (searchAppt.value.trim()) {
        const q = searchAppt.value.toLowerCase();
        list = list.filter(a => 
            String(a.id).includes(q) ||
            (a.mechanic_name || '').toLowerCase().includes(q) ||
            (a.service_details?.name || '').toLowerCase().includes(q)
        );
    }
    return list;
});

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
        case 'CONFIRMED': 
        case 'ON_THE_WAY':
        case 'IN_PROGRESS': return 'primary';
        case 'PENDING': return 'warning';
        case 'CANCELLED': return 'danger';
        default: return 'default';
    }
}

const translateStatus = (status) => {
    switch(status) {
        case 'PENDING': return 'Chờ nhận';
        case 'ACCEPTED': return 'Đã nhận';
        case 'ON_THE_WAY': return 'Đang đến';
        case 'IN_PROGRESS': return 'Đang sửa';
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

// ── Chat Logic ──
const showChat = ref(false);
const chatMessages = ref([]);
const newChatMessage = ref('');
const loadingChat = ref(false);
let chatPollInterval = null;
const activeChatBookingId = ref(null);

const openChat = async (item) => {
    activeChatBookingId.value = item.id;
    showChat.value = true;
    await fetchChats();
    startChatPolling();
    scrollToBottom();
};

const fetchChats = async () => {
    if (!activeChatBookingId.value) return;
    try {
        const res = await axios.get(`/api/bookings/${activeChatBookingId.value}/chat/`);
        const isNewMessage = chatMessages.value.length < res.data.length;
        chatMessages.value = res.data;
        if (isNewMessage) scrollToBottom();
    } catch (e) {
        console.error('Lỗi tải chat:', e);
    }
};

const sendChat = async () => {
    if (!newChatMessage.value.trim() || !activeChatBookingId.value) return;
    try {
        await axios.post(`/api/bookings/${activeChatBookingId.value}/chat/send/`, {
            text: newChatMessage.value.trim()
        });
        newChatMessage.value = '';
        await fetchChats();
    } catch (e) {
        showToast('Lỗi gửi tin nhắn');
    }
};

const startChatPolling = () => {
    if (chatPollInterval) return;
    chatPollInterval = setInterval(fetchChats, 3000); // poll every 3 seconds
};

const stopChatPolling = () => {
    if (chatPollInterval) {
        clearInterval(chatPollInterval);
        chatPollInterval = null;
    }
};

const scrollToBottom = () => {
    nextTick(() => {
        const scroller = document.getElementById('chat-body-scroller');
        if (scroller) scroller.scrollTop = scroller.scrollHeight;
    });
};

const closeChat = () => {
    showChat.value = false;
    stopChatPolling();
    activeChatBookingId.value = null;
};

// ── CANCEL WITH REASON ──
const showCancelDialog = ref(false);
const cancelReasonInput = ref('');
const cancellingId = ref(null);
const cancellingType = ref('SOS');

const cancelBooking = (id, type) => {
    cancellingId.value = id;
    cancellingType.value = type;
    cancelReasonInput.value = '';
    showCancelDialog.value = true;
};

const confirmCancel = async () => {
    if (!cancelReasonInput.value.trim()) {
        showFailToast('Vui lòng nhập lý do hủy');
        return;
    }
    try {
        const apiBase = cancellingType.value === 'SOS' ? '/api/bookings' : '/api/services';
        await axios.post(`${apiBase}/${cancellingId.value}/update-status/`, {
            status: 'CANCELLED',
            cancel_reason: cancelReasonInput.value.trim()
        });
        showToast('Đã hủy thành công');
        showCancelDialog.value = false;
        if (cancellingType.value === 'SOS') {
            const res = await axios.get('/api/bookings/history/');
            sosBookings.value = res.data;
        } else {
            const res = await axios.get('/api/services/history/');
            appointments.value = res.data;
        }
    } catch (e) {
        showToast('Lỗi khi hủy');
    }
};

// ── ORDER DETAIL POPUP ──
const showOrderDetail = ref(false);
const detailItem = ref(null);

const openDetail = (item) => {
    detailItem.value = item;
    showOrderDetail.value = true;
};

const detailTagType = computed(() => {
    if (!detailItem.value) return 'default';
    const s = detailItem.value.status;
    if (s === 'COMPLETED') return 'success';
    if (s === 'CANCELLED') return 'danger';
    if (s === 'PENDING') return 'warning';
    return 'primary';
});

// ── PAYMENT LOGIC ──
const showPayment = ref(false);
const paymentItem = ref(null);
const selectedPaymentMethod = ref('');
const paymentType = ref('SOS'); // 'SOS' or 'APPT'

const formatCost = (cost) => {
    if (!cost) return '0 VNĐ';
    return Number(cost).toLocaleString('vi-VN') + ' VNĐ';
};

const translatePaymentMethod = (method) => {
    if (method === 'CASH') return '(Tiền mặt)';
    if (method === 'TRANSFER') return '(Chuyển khoản)';
    return '';
};

const openPayment = (item) => {
    paymentItem.value = item;
    paymentType.value = 'SOS';
    selectedPaymentMethod.value = '';
    showPayment.value = true;
};

const openApptPayment = (appt) => {
    paymentItem.value = appt;
    paymentType.value = 'APPT';
    selectedPaymentMethod.value = '';
    showPayment.value = true;
};

const showQR = ref(false);
const qrUrl = ref('');
const paymentProcessing = ref(false);

const confirmPayment = async () => {
    if (!paymentItem.value || !selectedPaymentMethod.value) return;

    if (selectedPaymentMethod.value === 'TRANSFER') {
        const cost = paymentType.value === 'SOS' ? paymentItem.value.repair_cost : paymentItem.value.service_details?.price;
        const bankInfo = paymentItem.value.mechanic_bank_info;
        
        if (!bankInfo || !bankInfo.bank_name || !bankInfo.bank_account_no) {
            showFailToast('Vui lòng thanh toán Tiền mặt. Thợ này chưa cập nhật STK Ngân hàng!');
            return;
        }

        const bankId = bankInfo.bank_name.trim(); // e.g., 'MB', 'VCB'
        const accountNo = bankInfo.bank_account_no.trim();
        const accountName = bankInfo.bank_account_name ? bankInfo.bank_account_name.trim() : '';
        const addInfo = `Thanh toan don ${paymentType.value} ${paymentItem.value.id}`;
        
        qrUrl.value = `https://img.vietqr.io/image/${bankId}-${accountNo}-compact2.jpg?amount=${cost}&addInfo=${encodeURIComponent(addInfo)}&accountName=${encodeURIComponent(accountName)}`;
        
        showQR.value = true;
        showPayment.value = false;
        return;
    }

    await processPaymentAPI('CASH');
};

const processPaymentAPI = async (method) => {
    paymentProcessing.value = true;
    try {
        const apiBase = paymentType.value === 'SOS' ? '/api/bookings' : '/api/services';
        await axios.post(`${apiBase}/${paymentItem.value.id}/confirm-payment/`, {
            payment_method: method
        });
        showSuccessToast('Thanh toán thành công!');
        showQR.value = false;
        showPayment.value = false;
        
        if (paymentType.value === 'SOS') {
            const res = await axios.get('/api/bookings/history/');
            sosBookings.value = res.data;
        } else {
            const res = await axios.get('/api/services/history/');
            appointments.value = res.data;
        }
    } catch (e) {
        if (e.response && e.response.data && e.response.data.error) {
            showFailToast(e.response.data.error);
        } else {
            showFailToast('Lỗi xác nhận thanh toán');
        }
    } finally {
        paymentProcessing.value = false;
    }
};

// ── REAL-TIME TRACKING LOGIC ──
const showTracking = ref(false);
const trackingBookingId = ref(null);
const trackingStatus = ref('pending');
const trackingStatusText = ref('Đang chờ...');
const trackingMechanicName = ref('');
let trackingMap = null;
let trackingMechMarker = null;
let trackingCustMarker = null;
let trackingRoute = null;       // Routing control (created once)
let trackingPolyline = null;    // Lightweight polyline for smooth updates
let trackingInterval = null;
let isFirstTrackingLoad = true; // Only fitBounds on first load

const statusTextMap = {
    'PENDING': 'Chờ nhận đơn',
    'ACCEPTED': 'Thợ đã nhận đơn',
    'ON_THE_WAY': 'Thợ đang trên đường đến',
    'IN_PROGRESS': 'Thợ đang sửa xe',
    'COMPLETED': 'Hoàn thành',
};

const openTracking = (item) => {
    trackingBookingId.value = item.id;
    trackingMechanicName.value = item.mechanic_name || 'Thợ #' + item.mechanic;
    trackingStatus.value = item.status.toLowerCase();
    trackingStatusText.value = statusTextMap[item.status] || item.status;
    isFirstTrackingLoad = true;
    showTracking.value = true;
};

// Icon definitions (reusable, avoid re-creating every cycle)
const custIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41], iconAnchor: [12, 41]
});
const mechIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41], iconAnchor: [12, 41]
});

const initTrackingMap = async () => {
    await new Promise(r => setTimeout(r, 300));

    if (!trackingMap) {
        trackingMap = L.map('tracking-map').setView([21.0285, 105.8542], 14);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }).addTo(trackingMap);
    }

    trackingMap.invalidateSize();
    await fetchTrackingData();
    startTrackingPolling();
};

const fetchTrackingData = async () => {
    if (!trackingBookingId.value) return;
    try {
        const res = await axios.get(`/api/bookings/${trackingBookingId.value}/tracking/`);
        const data = res.data;

        trackingStatus.value = data.status.toLowerCase();
        trackingStatusText.value = statusTextMap[data.status] || data.status;

        const mechLat = data.mechanic.latitude;
        const mechLon = data.mechanic.longitude;
        const custLat = data.customer.latitude;
        const custLon = data.customer.longitude;

        if (data.mechanic.username) {
            trackingMechanicName.value = data.mechanic.username;
        }

        // ── Customer marker (create once) ──
        if (custLat && custLon && !trackingCustMarker) {
            trackingCustMarker = L.marker([custLat, custLon], { icon: custIcon })
                .addTo(trackingMap)
                .bindPopup('📍 Vị trí của bạn');
        }

        // ── Mechanic marker (create once, then smoothly move) ──
        if (mechLat && mechLon) {
            if (!trackingMechMarker) {
                trackingMechMarker = L.marker([mechLat, mechLon], { icon: mechIcon })
                    .addTo(trackingMap)
                    .bindPopup('🔧 ' + trackingMechanicName.value);
            } else {
                trackingMechMarker.setLatLng([mechLat, mechLon]);
            }

            // ── Route: create Routing control ONCE on first load, then update polyline ──
            if (custLat && custLon) {
                if (isFirstTrackingLoad) {
                    // First load: create full Routing control + fitBounds
                    if (trackingRoute) {
                        trackingMap.removeControl(trackingRoute);
                        trackingRoute = null;
                    }
                    trackingRoute = L.Routing.control({
                        waypoints: [
                            L.latLng(mechLat, mechLon),
                            L.latLng(custLat, custLon)
                        ],
                        routeWhileDragging: false,
                        addWaypoints: false,
                        createMarker: () => null,
                        lineOptions: {
                            styles: [{ color: '#2563eb', opacity: 0.8, weight: 5 }]
                        },
                        show: false
                    }).addTo(trackingMap);

                    // Fit bounds only on first load
                    const group = new L.featureGroup([
                        L.marker([mechLat, mechLon]),
                        L.marker([custLat, custLon])
                    ]);
                    trackingMap.fitBounds(group.getBounds(), { padding: [50, 50] });
                    isFirstTrackingLoad = false;
                } else {
                    // Subsequent polls: just update waypoints silently (no rebuild, no zoom reset)
                    if (trackingRoute) {
                        trackingRoute.setWaypoints([
                            L.latLng(mechLat, mechLon),
                            L.latLng(custLat, custLon)
                        ]);
                    }
                }
            }
        }

        // If booking completed, stop polling and refresh history
        if (data.status === 'COMPLETED' || data.status === 'CANCELLED') {
            stopTrackingPolling();
            const refreshRes = await axios.get('/api/bookings/history/');
            sosBookings.value = refreshRes.data;
        }

    } catch (e) {
        console.error('Tracking fetch error:', e);
    }
};

const startTrackingPolling = () => {
    if (trackingInterval) return;
    trackingInterval = setInterval(fetchTrackingData, 5000);
};

const stopTrackingPolling = () => {
    if (trackingInterval) {
        clearInterval(trackingInterval);
        trackingInterval = null;
    }
    // Clean up map layers for next opening
    if (trackingMechMarker) { trackingMap?.removeLayer(trackingMechMarker); trackingMechMarker = null; }
    if (trackingCustMarker) { trackingMap?.removeLayer(trackingCustMarker); trackingCustMarker = null; }
    if (trackingRoute) { trackingMap?.removeControl(trackingRoute); trackingRoute = null; }
    if (trackingPolyline) { trackingMap?.removeLayer(trackingPolyline); trackingPolyline = null; }
    isFirstTrackingLoad = true;
};

onUnmounted(() => {
    stopTrackingPolling();
    stopChatPolling();
});
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
    border-radius: 16px;
    margin-bottom: 12px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0,0,0,0.04);
    border: 1px solid #f0f2f5;
    transition: box-shadow 0.2s;
}
.ai-history-card:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}

.aih-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
}
/* Severity left strip - now a ring or soft border */
.aih-strip {
    width: 6px;
    height: 44px;
    border-radius: 8px;
    flex-shrink: 0;
}
.aih-low    { background: linear-gradient(180deg, #10b981, #059669); }
.aih-medium { background: linear-gradient(180deg, #fbbf24, #d97706); }
.aih-high   { background: linear-gradient(180deg, #ef4444, #dc2626); }
.aih-critical { background: linear-gradient(180deg, #65a30d, #4d7c0f); } /* Dark green or dark red depending on intended design */

.aih-meta { flex: 1; min-width: 0; }
.aih-diagnosis {
    display: flex;
    align-items: center;
    font-size: 15px;
    font-weight: 700;
    color: #1a1a2e;
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.aih-date { display: block; font-size: 11px; color: #999; margin-top: 4px; font-weight: 500; }

/* Custom Badge Setup */
.aih-badge {
    flex-shrink: 0;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.2px;
}
.badge-safe {
    background: #ecfdf5;
    color: #059669;
    border: 1px solid #a7f3d0;
}
.badge-danger {
    background: #fef2f2;
    color: #dc2626;
    border: 1px solid #fecaca;
}

.aih-detail {
    font-size: 13px;
    color: #555;
    line-height: 1.6;
    padding: 0 16px 14px;
    margin: 0 16px;
    border-bottom: 1px dashed #e5e7eb;
}

.aih-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: #fcfcfc;
}
.aih-price { font-size: 14px; font-weight: 700; color: #2563eb; }

/* ── Tracking Popup (Grab-style) ── */
.tracking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 10px;
  border-bottom: 1px solid #f0f0f0;
}
.tracking-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
}
.tracking-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  display: inline-block;
  animation: pulse-dot 1.5s infinite;
}
.tracking-dot.on_the_way { background: #2563eb; }
.tracking-dot.in_progress { background: #07c160; }
.tracking-dot.accepted { background: #ff976a; }
.tracking-dot.pending { background: #ccc; }

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.4); }
}

.tracking-map {
  width: 100%;
  height: calc(100% - 120px);
  z-index: 1;
}

.tracking-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fff;
}
.tracking-mechanic {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
}
.tracking-badge { }

/* Status chip colors for new statuses */
.chip-on_the_way { background: #dbeafe; color: #2563eb; }
.chip-in_progress { background: #d4fae4; color: #07c160; }

/* ── Payment Popup ── */
.payment-container {
  padding: 24px 20px;
  text-align: center;
}
.payment-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 12px;
}
.payment-amount {
  font-size: 28px;
  font-weight: 800;
  color: #e74c3c;
  margin-bottom: 16px;
}
.payment-subtitle {
  font-size: 14px;
  color: #888;
  margin-bottom: 16px;
}
.payment-methods {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}
.payment-method-card {
  flex: 1;
  padding: 16px 12px;
  border: 2px solid #eee;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}
.payment-method-card.active {
  border-color: #07c160;
  background: #f0fff8;
  box-shadow: 0 2px 12px rgba(7, 193, 96, 0.15);
}
.pm-icon { font-size: 28px; display: block; margin-bottom: 6px; }
.pm-label { font-size: 14px; font-weight: 600; color: #333; }

.paid-badge {
  font-size: 11px;
  color: #07c160;
  font-weight: 700;
  background: #f0fff8;
  padding: 3px 8px;
  border-radius: 20px;
}

/* ── Order Detail Popup ── */
.detail-container { padding: 0; }
.detail-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 20px 12px; border-bottom: 1px solid #f0f0f0;
}
.detail-title { font-size: 17px; font-weight: 700; color: #1a1a2e; margin: 0; }
.detail-body { padding: 12px 20px; }
.detail-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 0; border-bottom: 1px solid #f5f5f5;
}
.detail-row:last-child { border-bottom: none; }
.detail-label { font-size: 13px; color: #888; font-weight: 500; }
.detail-value { font-size: 13px; color: #333; font-weight: 600; text-align: right; max-width: 60%; }
.detail-value.cost { color: #e74c3c; font-size: 15px; font-weight: 800; }
.detail-row.highlight { background: #fffbeb; margin: 0 -20px; padding: 12px 20px; }
.detail-row.cancel { background: #fff5f5; margin: 0 -20px; padding: 12px 20px; }
.detail-row.cancel .detail-value { color: #e74c3c; }

.hst-card-header { cursor: pointer; }

/* ── Filter Bar ── */
.filter-bar { padding: 10px 12px 4px; }
.filter-bar .van-field { background: #f5f5f5; border-radius: 10px; margin-bottom: 8px; }
.filter-pills { display: flex; gap: 6px; flex-wrap: wrap; }
.pill {
  font-size: 12px; padding: 4px 12px; border-radius: 20px;
  background: #f0f0f0; color: #888; cursor: pointer;
  font-weight: 600; transition: all 0.2s;
}
.pill.active { background: #2563eb; color: #fff; }

/* ─── Modern Buttons Override ─── */
:deep(.van-button) {
  border-radius: 8px;
  font-weight: 600;
  border: none !important;
  transition: all 0.2s ease;
  padding: 0 16px;
}
:deep(.van-button:active) {
  transform: scale(0.96);
}
:deep(.van-button--primary:not(.van-button--plain)) {
  background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
  color: #fff !important;
}
:deep(.van-button--success:not(.van-button--plain)) {
  background: linear-gradient(135deg, #059669, #10b981) !important;
  box-shadow: 0 4px 10px rgba(16, 185, 129, 0.25);
  color: #fff !important;
}
:deep(.van-button--warning:not(.van-button--plain)) {
  background: linear-gradient(135deg, #ea580c, #f97316) !important;
  box-shadow: 0 4px 10px rgba(249, 115, 22, 0.25);
  color: #fff !important;
}
:deep(.van-button--danger:not(.van-button--plain)) {
  background: linear-gradient(135deg, #e11d48, #f43f5e) !important;
  box-shadow: 0 4px 10px rgba(244, 63, 94, 0.25);
  color: #fff !important;
}
/* Plain buttons styling */
:deep(.van-button--primary.van-button--plain) {
  background: #eff6ff !important;
  color: #2563eb !important;
}
:deep(.van-button--warning.van-button--plain) {
  background: #fff7ed !important;
  color: #ea580c !important;
}
:deep(.van-button--success.van-button--plain) {
  background: #ecfdf5 !important;
  color: #059669 !important;
}
:deep(.van-button--danger.van-button--plain) {
  background: #fff1f2 !important;
  color: #e11d48 !important;
}

/* CHAT POPUP */
.chat-header {
  padding: 16px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center; background: #fff; border-radius: 20px 20px 0 0;
}
.chat-body {
  flex: 1; overflow-y: auto; padding: 16px; background: #f9f9f9; display: flex; flex-direction: column; gap: 10px;
}
.chat-msg { display: flex; flex-direction: column; max-width: 80%; }
.chat-msg.msg-me { align-self: flex-end; align-items: flex-end; }
.chat-msg.msg-them { align-self: flex-start; align-items: flex-start; }
.msg-bubble {
  padding: 10px 14px; border-radius: 16px; font-size: 14px; line-height: 1.4; position: relative;
}
.msg-me .msg-bubble { background: #1989fa; color: #fff; border-bottom-right-radius: 4px; }
.msg-them .msg-bubble { background: #fff; color: #333; border: 1px solid #eaeaea; border-bottom-left-radius: 4px; }
.msg-time { font-size: 10px; opacity: 0.7; margin-top: 4px; text-align: right; }
.msg-them .msg-time { text-align: left; }
.chat-footer {
  padding: 10px 16px; background: #fff; border-top: 1px solid #f0f0f0; display: flex; align-items: center;
}
.chat-footer .van-field { background: #f5f5f5; border-radius: 20px; padding: 8px 16px; flex: 1; }

</style>
