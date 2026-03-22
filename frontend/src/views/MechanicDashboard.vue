<template>
  <div class="mechanic-container">
    <van-nav-bar title="Dashboard Thợ">
      <template #right>
        <van-icon name="setting-o" size="20" @click="$router.push('/mechanic/profile')" />
      </template>
    </van-nav-bar>

    <!-- Banner Trạng thái -->
    <van-notice-bar
      :text="isAvailable ? 'Bạn đang SẴN SÀNG nhận đơn' : 'Bạn đang NGHỆ - Không nhận đơn'"
      :color="isAvailable ? '#07c160' : '#ee0a24'"
      :background="isAvailable ? '#f0fff8' : '#fff0f0'"
      left-icon="clock-o"
    >
      <template #right-icon>
        <van-switch v-model="isAvailable" size="18px" @change="updateAvailability" />
      </template>
    </van-notice-bar>
    
    <van-tabs v-model:active="activeTab" @change="refreshData">
        <van-tab name="SOS">
            <template #title>
                <div style="height: 100%; display: flex; align-items: center; justify-content: center;">
                    <span style="position: relative; padding: 8px 12px; font-weight: 600;">
                        SOS
                        <span v-if="pendingCount > 0" style="position: absolute; top: 0; right: 0; background: #ee0a24; color: #fff; font-size: 10px; font-weight: bold; border-radius: 10px; padding: 2px 4px; line-height: 1; border: 1px solid #fff;">
                            {{ pendingCount }}
                        </span>
                    </span>
                </div>
            </template>
        </van-tab>
        <van-tab title="Lịch Hẹn" name="APPT"></van-tab>
        <van-tab name="PAYMENT">
            <template #title>
                <div style="height: 100%; display: flex; align-items: center; justify-content: center;">
                    <span style="position: relative; padding: 8px 12px; font-weight: 600;">
                        Thanh Toán
                        <span v-if="pendingPaymentCount > 0" style="position: absolute; top: 0; right: 0; background: #ee0a24; color: #fff; font-size: 10px; font-weight: bold; border-radius: 10px; padding: 2px 4px; line-height: 1; border: 1px solid #fff;">
                            {{ pendingPaymentCount }}
                        </span>
                    </span>
                </div>
            </template>
        </van-tab>
        <van-tab title="Thống Kê" name="STATS"></van-tab>
    </van-tabs>

    <!-- NỘI DUNG TAB SOS -->
    <div v-if="activeTab === 'SOS'" class="p-2">
         <van-tabs v-model:active="sosSubTab">
            <van-tab title="Mới" name="PENDING"></van-tab>
            <van-tab title="Đang làm" name="ACTIVE"></van-tab>
         </van-tabs>

         <div v-if="loadingSOS" class="text-center p-4">Đang tải SOS...</div>
         <van-empty v-if="!loadingSOS && filteredSOS.length === 0" description="Không có đơn SOS nào" />
         
         <van-card
            v-for="item in filteredSOS"
            :key="'sos-'+item.id"
            :tag="translateStatus(item.status)"
            :price="item.problem_description"
            :thumb="'https://img.freepik.com/free-icon/user_318-159711.jpg'"
        >
            <template #title>
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px; padding-top: 4px;">
                    Khách: {{ item.customer_name || '#' + item.customer }}
                </div>
            </template>
            <template #desc>
                <div style="color: #666; font-size: 12px; margin-bottom: 6px;">
                    MBD: {{ formatOrderId(item.id, 'SOS') }}
                </div>
            </template>
            <template #tags>
                <div v-if="item.damage_image" class="mt-2" style="display: flex; gap: 8px; align-items: center;">
                  <span style="font-size: 12px; color: #888;">Ảnh sự cố:</span>
                  <van-image width="50" height="50" radius="4" :src="item.damage_image" fit="cover" @click.stop="previewImage(item.damage_image)" />
                </div>
            </template>
            <template #footer>
                <van-button v-if="item.status === 'PENDING'" size="small" type="primary" @click="updateSOSStatus(item.id, 'ACCEPTED')">Nhận Đơn</van-button>
                <div v-if="item.status === 'ACCEPTED'">
                    <van-button size="small" type="primary" plain icon="chat-o" @click="openChat(item)" style="margin-right:4px">Chat</van-button>
                    <van-button size="small" type="warning" plain @click="viewRoute(item)" style="margin-right:4px">Đường</van-button>
                    <van-button size="small" type="primary" @click="updateSOSStatus(item.id, 'ON_THE_WAY')" style="margin-right:4px">Đi</van-button>
                    <van-button size="small" type="danger" plain @click="openComplaint(item, 'SOS')">Báo cáo</van-button>
                </div>
                <div v-if="item.status === 'ON_THE_WAY'">
                    <van-button size="small" type="primary" plain icon="chat-o" @click="openChat(item)" style="margin-right:4px">Chat</van-button>
                    <van-button size="small" type="warning" plain @click="viewRoute(item)" style="margin-right:4px">Đường</van-button>
                    <van-button size="small" type="primary" @click="updateSOSStatus(item.id, 'IN_PROGRESS')" style="margin-right:4px">Tới</van-button>
                    <van-button size="small" type="danger" plain @click="openComplaint(item, 'SOS')">Báo cáo</van-button>
                </div>
                <div v-if="item.status === 'IN_PROGRESS'">
                    <van-button size="small" type="primary" plain icon="chat-o" @click="openChat(item)" style="margin-right:4px">Chat</van-button>
                    <van-button size="small" type="success" @click="openCostDialog(item)" style="margin-right:4px">Tính Tiền</van-button>
                    <van-button size="small" type="danger" plain @click="openComplaint(item, 'SOS')">Báo cáo</van-button>
                </div>
            </template>
        </van-card>
    </div>

    <!-- NỘI DUNG TAB LỊCH HẸN -->
    <div v-if="activeTab === 'APPT'" class="p-2">
         <div v-if="loadingAppt" class="text-center p-4">Đang tải lịch hẹn...</div>
         <van-empty v-if="!loadingAppt && appointments.length === 0" description="Không có lịch hẹn nào" />

         <van-card
            v-for="item in appointments"
            :key="'appt-'+item.id"
            :tag="translateStatus(item.status)"
            :price="item.service_details.name"
            thumb="https://img.freepik.com/free-vector/date-picker-concept-illustration_114360-4668.jpg"
        >
            <template #title>
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px; padding-top: 4px;">
                    Hẹn: {{ formatDate(item.appointment_time) }}
                </div>
            </template>
            <template #desc>
                <div style="color: #666; font-size: 12px; margin-bottom: 6px;">
                    MBD: {{ formatOrderId(item.id, 'BD') }}<br>
                    Khách: {{ item.customer_name || '#' + item.customer }}
                </div>
            </template>
            <template #tags>
                <div class="mt-1">Ghi chú: {{ item.note || 'Không có' }}</div>
            </template>
            <template #footer>
                <van-button v-if="item.status === 'PENDING'" size="small" type="primary" @click="updateApptStatus(item.id, 'CONFIRMED')">Xác Nhận</van-button>
                <div v-if="item.status === 'CONFIRMED'">
                     <van-button size="small" type="success" @click="updateApptStatus(item.id, 'COMPLETED')" style="margin-right:4px">Hoàn Thành</van-button>
                     <van-button size="small" type="danger" @click="updateApptStatus(item.id, 'CANCELLED')" style="margin-right:4px">Hủy</van-button>
                     <van-button size="small" type="danger" plain @click="openComplaint(item, 'APPT')">Báo cáo</van-button>
                </div>
            </template>
        </van-card>
    </div>

    <!-- NỘI DUNG TAB THANH TOÁN -->
    <div v-if="activeTab === 'PAYMENT'" class="p-2">
        <van-empty v-if="pendingPayments.length === 0" description="Không có khoản nào chờ thanh toán" />
        <van-card v-for="item in pendingPayments" :key="item.type + item.id"
            :tag="'Chờ nhận tiền'"
            :price="item.amount"
            thumb="https://img.freepik.com/free-icon/money_318-550990.jpg"
        >
            <template #title>
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px; padding-top: 4px;">
                    {{ item.type === 'SOS' ? item.problem_description : item.service_name }}
                </div>
            </template>
            <template #desc>
                <div style="color: #666; font-size: 12px; margin-bottom: 6px;">
                    MBD: {{ formatOrderId(item.id, item.type === 'SOS' ? 'SOS' : 'BD') }}<br>
                    Khách: {{ item.customer_name || '#' + item.customer }}
                </div>
            </template>
            <template #tags>
                <div class="mt-1" style="color:#ee0a24">Chờ bạn xác nhận tiền vào TK Ngân hàng</div>
            </template>
            <template #footer>
                <div style="text-align: right;">
                    <van-button size="small" type="danger" plain @click="rejectPayment(item)" style="margin-right: 8px;">Chưa nhận được</van-button>
                    <van-button size="small" type="success" @click="verifyPayment(item)">Đã Nhận Tiền</van-button>
                </div>
            </template>
        </van-card>
    </div>

    <!-- NỘI DUNG TAB THỐNG KÊ -->
    <div v-if="activeTab === 'STATS'">
        <StatsCharts />
    </div>

    <!-- DIALOG CHỈ ĐƯỜNG TRÊN BẢN ĐỒ -->
    <van-popup v-model:show="showMap" position="bottom" :style="{ height: '80%' }" @opened="initMap">
        <div class="map-header">
            <span class="title">Bản Đồ Chỉ Đường</span>
            <van-icon name="cross" size="20" @click="showMap = false" />
        </div>
        <div id="mechanic-map" style="width: 100%; height: calc(100% - 40px);"></div>
    </van-popup>

    <!-- DIALOG NHẬP CHI PHÍ SỬA CHỮA -->
    <van-dialog v-model:show="showCostDialog" title="Nhập Chi Phí Sửa Chữa" show-cancel-button 
      confirm-button-text="Hoàn Thành" cancel-button-text="Hủy" @confirm="submitCompletion">
      <div style="padding: 20px;">
        <van-field v-model="repairCostInput" type="digit" label="Số tiền (VNĐ)" 
          placeholder="VD: 250000" input-align="right" />
        <p style="font-size: 12px; color: #999; margin-top: 10px; text-align: center;">
          Khách hàng sẽ nhìn thấy số tiền này và chọn hình thức thanh toán.
        </p>
      </div>
    </van-dialog>

    <!-- DIALOG KHIẾU NẠI CHO THỢ -->
    <van-dialog v-model:show="showComplaint" title="Báo Cáo Khách Hàng" show-cancel-button
      confirm-button-text="Gửi Báo Cáo" cancel-button-text="Hủy" @confirm="submitComplaint">
      <div style="padding: 16px;">
        <p style="font-size:13px; color:#666; margin-top:0;">Nếu khách hàng có dấu hiệu bom hàng, boom xe, chửi bới, báo cáo sai sự thật, hãy ghi rõ để hệ thống xử lý.</p>
        <van-field v-model="complaintReason" type="textarea" rows="4"
          placeholder="Nhập lý do báo cáo (bắt buộc)..." maxlength="500" show-word-limit
          style="border: 1px solid #eee; border-radius: 4px;" />
      </div>
    </van-dialog>

    <!-- POPUP CHAT -->
    <van-popup v-model:show="showChat" position="bottom" :style="{ height: '80%', display: 'flex', flexDirection: 'column' }" round>
      <div class="chat-header">
        <h3 style="margin:0; font-size:16px; display:flex; align-items:center; gap:6px;">
          <van-icon name="chat-o" size="18" /> Chat với Khách
        </h3>
        <van-icon name="cross" size="18" @click="closeChat" />
      </div>
      <div class="chat-body" id="chat-body-scroller">
        <div v-if="loadingChat" class="text-center p-4">Đang tải...</div>
        <div v-for="msg in chatMessages" :key="msg.id" class="chat-msg" :class="!msg.is_mechanic ? 'msg-them' : 'msg-me'">
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
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import axios from 'axios';
import { showToast, showImagePreview } from 'vant';
import L from 'leaflet';
import 'leaflet-routing-machine';
import 'leaflet-routing-machine/dist/leaflet-routing-machine.css';
import StatsCharts from '../components/StatsCharts.vue';

const activeTab = ref('SOS');
const sosSubTab = ref('PENDING');

const sosBookings = ref([]);
const appointments = ref([]);
const stats = ref({});
const loadingSOS = ref(false);
const loadingAppt = ref(false);
const loadingStats = ref(false);

const formatOrderId = (id, prefix) => {
    return `${prefix}-${String(id).padStart(5, '0')}`;
};

// Trạng thái khả dụng (nhận đơn)
const isAvailable = ref(true);
onMounted(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            if (user.mechanic_profile) {
                isAvailable.value = user.mechanic_profile.is_available;
            }
        } catch(e) {}
    }
});

const updateAvailability = async (val) => {
    try {
        const res = await axios.post('/api/users/mechanic/status/', { is_available: val });
        // Cập nhật localStorage
        const userStr = localStorage.getItem('user');
        if (userStr) {
            const user = JSON.parse(userStr);
            if (user.mechanic_profile) user.mechanic_profile.is_available = val;
            localStorage.setItem('user', JSON.stringify(user));
        }
        showToast(val ? 'Đã bật nhận đơn' : 'Đã tắt nhận đơn');
    } catch(e) {
        showToast('Lỗi cập nhật trạng thái');
        isAvailable.value = !val; // Hoàn tác thao tác công tắc
    }
}

// Trạng thái Bản đồ
const showMap = ref(false);
let mapInstance = null;
let routingControl = null;
const activeRouteItem = ref(null);

const fetchSOS = async (isBackground = false) => {
    if (!isBackground) loadingSOS.value = true;
    try {
        const res = await axios.get('/api/bookings/mechanic/list/');
        sosBookings.value = res.data;
    } catch (e) {
        console.error(e);
    } finally {
        if (!isBackground) loadingSOS.value = false;
    }
}

const fetchAppt = async (isBackground = false) => {
    if (!isBackground) loadingAppt.value = true;
    try {
        const res = await axios.get('/api/services/mechanic/list/');
        appointments.value = res.data;
    } catch (e) {
        console.error(e);
    } finally {
        if (!isBackground) loadingAppt.value = false;
    }
}

const fetchStats = async (isBackground = false) => {
    if (!isBackground) loadingStats.value = true;
    try {
        const res = await axios.get('/api/services/mechanic/revenue/');
        stats.value = res.data;
    } catch (e) {
        console.error(e);
    } finally {
        if (!isBackground) loadingStats.value = false;
    }
}

const refreshData = () => {
    if (activeTab.value === 'SOS') fetchSOS();
    else if (activeTab.value === 'APPT') fetchAppt();
    else fetchStats();
}

// Tải lần đầu + tự động kiểm tra định kỳ các đơn SOS mới
let sosAutoRefresh = null;

const pendingCount = computed(() => {
    return sosBookings.value.filter(b => b.status === 'PENDING').length;
});

onMounted(() => {
    refreshData();
    // Yêu cầu quyền Thông báo từ trình duyệt
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    // Tự động làm mới SOS mỗi 15 giây để kiểm tra đơn mới
    sosAutoRefresh = setInterval(async () => {
        if (activeTab.value === 'SOS') {
            const prevCount = sosBookings.value.filter(b => b.status === 'PENDING').length;
            await fetchSOS(true);
            const newCount = sosBookings.value.filter(b => b.status === 'PENDING').length;
            if (newCount > prevCount && 'Notification' in window && Notification.permission === 'granted') {
                new Notification('🚨 Đơn SOS mới!', { body: `Bạn có ${newCount} đơn chờ xác nhận.` });
            }
        }
    }, 15000);
});

onUnmounted(() => {
    stopGPSSender();
    if (sosAutoRefresh) { clearInterval(sosAutoRefresh); sosAutoRefresh = null; }
    stopChatPolling();
});

const filteredSOS = computed(() => {
    if (sosSubTab.value === 'ACTIVE') {
        return sosBookings.value.filter(b => ['ACCEPTED', 'ON_THE_WAY', 'IN_PROGRESS'].includes(b.status));
    }
    return sosBookings.value.filter(b => b.status === sosSubTab.value);
});

const pendingPayments = computed(() => {
    const sos = sosBookings.value.filter(b => b.status === 'COMPLETED' && b.payment_status === 'PENDING').map(b => ({
        ...b,
        type: 'SOS',
        amount: b.repair_cost
    }));
    const appts = appointments.value.filter(b => b.status === 'COMPLETED' && b.payment_status === 'PENDING').map(b => ({
        ...b,
        type: 'APPT',
        amount: b.service_details?.price,
        service_name: b.service_details?.name
    }));
    return [...sos, ...appts];
});

const pendingPaymentCount = computed(() => pendingPayments.value.length);

const verifyPayment = async (item) => {
    try {
        const url = item.type === 'SOS' 
            ? `/api/bookings/${item.id}/verify-payment/` 
            : `/api/services/${item.id}/verify-payment/`;
        await axios.post(url);
        showToast('Xác nhận nhận tiền thành công!');
        fetchSOS();
        fetchAppt();
    } catch (e) {
        showToast('Lỗi xác nhận thanh toán');
    }
};

const rejectPayment = async (item) => {
    try {
        const url = item.type === 'SOS' 
            ? `/api/bookings/${item.id}/reject-payment/` 
            : `/api/services/${item.id}/reject-payment/`;
        await axios.post(url);
        showToast('Đã thông báo Chưa nhận được tiền!');
        fetchSOS();
        fetchAppt();
    } catch (e) {
        showToast('Lỗi từ chối thanh toán');
    }
};

const updateSOSStatus = async (id, newStatus) => {
    try {
        await axios.post(`/api/bookings/${id}/update-status/`, { status: newStatus });
        showToast('Cập nhật SOS thành công!');
        // Bắt đầu gửi GPS khi thợ đang ĐANG ĐẾN hoặc ĐANG SỬA
        if (newStatus === 'ON_THE_WAY' || newStatus === 'IN_PROGRESS') {
            startGPSSender();
        }
        // Dừng gửi GPS khi hoàn thành đơn hoặc hủy bỏ
        if (newStatus === 'COMPLETED' || newStatus === 'CANCELLED') {
            stopGPSSender();
        }
        fetchSOS();
    } catch (e) {
        showToast('Lỗi cập nhật SOS');
    }
}

// ── Logic Chat ──
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
    chatPollInterval = setInterval(fetchChats, 3000); // gọi API mỗi 3 giây
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

const previewImage = (url) => {
    if (!url) return;
    showImagePreview([url]);
};

// ── Dialog Nhập giá sửa chữa ──
const showCostDialog = ref(false);
const repairCostInput = ref('');
const completingBookingId = ref(null);

const openCostDialog = (item) => {
    completingBookingId.value = item.id;
    repairCostInput.value = '';
    showCostDialog.value = true;
};

const submitCompletion = async () => {
    if (!repairCostInput.value || parseInt(repairCostInput.value) <= 0) {
        showToast('Vui lòng nhập số tiền hợp lệ');
        return;
    }
    try {
        await axios.post(`/api/bookings/${completingBookingId.value}/update-status/`, {
            status: 'COMPLETED',
            repair_cost: parseInt(repairCostInput.value)
        });
        showToast('Hoàn thành! Khách hàng sẽ nhận được thông báo thanh toán.');
        stopGPSSender();
        fetchSOS();
    } catch (e) {
        showToast('Lỗi hoàn thành đơn');
    }
};
// ── Gửi vị trí GPS thời gian thực ──
let gpsWatchId = null;
let gpsSendInterval = null;
const currentGPS = ref({ lat: null, lon: null });

const startGPSSender = () => {
    if (gpsSendInterval) return; // Đã đang gửi tọa độ rồi

    // Theo dõi vị trí sử dụng Geolocation của HTML5
    if (navigator.geolocation) {
        gpsWatchId = navigator.geolocation.watchPosition(
            (pos) => {
                currentGPS.value.lat = pos.coords.latitude;
                currentGPS.value.lon = pos.coords.longitude;
            },
            (err) => {
                console.warn('Lỗi định vị GPS:', err.message);
            },
            { enableHighAccuracy: true, maximumAge: 5000 }
        );
    }

    // Gửi vị trí tới server mỗi 10 giây
    gpsSendInterval = setInterval(async () => {
        if (currentGPS.value.lat && currentGPS.value.lon) {
            try {
                await axios.post('/api/users/mechanic/update-location/', {
                    latitude: currentGPS.value.lat,
                    longitude: currentGPS.value.lon
                });
            } catch (e) {
                // Lỗi im lặng - không làm phiền thợ
            }
        }
    }, 10000);
};

const stopGPSSender = () => {
    if (gpsWatchId !== null) {
        navigator.geolocation.clearWatch(gpsWatchId);
        gpsWatchId = null;
    }
    if (gpsSendInterval) {
        clearInterval(gpsSendInterval);
        gpsSendInterval = null;
    }
};

onUnmounted(() => {
    stopGPSSender();
});

const updateApptStatus = async (id, status) => {
    try {
        await axios.post(`/api/services/${id}/update-status/`, { status });
        showToast('Cập nhật Lịch hẹn thành công!');
        fetchAppt();
    } catch (e) {
        showToast('Lỗi cập nhật Lịch hẹn');
    }
}

// ── KHIẾU NẠI DÀNH CHO THỢ ──
const showComplaint = ref(false);
const complaintReason = ref('');
const complaintTargetId = ref(null);
const complaintTargetType = ref('SOS');

const openComplaint = (item, type) => {
    complaintTargetId.value = item.id;
    complaintTargetType.value = type;
    complaintReason.value = '';
    showComplaint.value = true;
};

const submitComplaint = async () => {
    if (!complaintReason.value.trim()) {
        showToast('Vui lòng nhập lý do báo cáo');
        return;
    }
    try {
        const payload = {
            reason: complaintReason.value.trim()
        };
        // Backend tự gán accused_user = customer thông qua booking id
        if (complaintTargetType.value === 'SOS') {
            payload.booking = complaintTargetId.value;
        }

        await axios.post('/api/bookings/complaints/', payload);
        showToast({ message: 'Đã gửi báo cáo thành công.', type: 'success' });
        showComplaint.value = false;
    } catch (e) {
        if (e.response && e.response.data && e.response.data.error) {
            showToast('Lỗi: ' + e.response.data.error);
        } else {
            showToast('Lỗi gửi báo cáo');
        }
    }
};

// ── LOGIC CHỈ ĐƯỜNG BẢN ĐỒ ──
const viewRoute = (item) => {
    activeRouteItem.value = item;
    showMap.value = true;
}

const initMap = async () => {
    if (!mapInstance) {
        mapInstance = L.map('mechanic-map');
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(mapInstance);
    }

    // Xóa các điều khiển và lớp chỉ đường trước đó
    if (routingControl) {
        mapInstance.removeControl(routingControl);
        routingControl = null;
    }
    mapInstance.eachLayer((layer) => {
        if (layer instanceof L.Marker) {
            mapInstance.removeLayer(layer);
        }
    });

    const item = activeRouteItem.value;
    if (!item) return;

    // Lấy vị trí hiện tại của Thợ từ thông tin profile người dùng
    const userStr = localStorage.getItem('user');
    
    // Chuyển đổi định dạng số thực một cách an toàn
    const custLat = parseFloat(item.customer_lat);
    const custLon = parseFloat(item.customer_lon);

    // Giả lập tọa độ của thợ hơi xê dịch (nếu chưa có thiết bị GPS thật)
    let mechLat = custLat - 0.005; 
    let mechLon = custLon - 0.005; 

    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            if (user.mechanic_profile && user.mechanic_profile.latitude) {
                mechLat = parseFloat(user.mechanic_profile.latitude);
                mechLon = parseFloat(user.mechanic_profile.longitude);
            }
        } catch(e) {}
    }

    const mechIcon = L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
      iconSize: [25, 41], iconAnchor: [12, 41]
    });
    const custIcon = L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
      iconSize: [25, 41], iconAnchor: [12, 41]
    });

    // Sử dụng leaflet-routing-machine để hiện lộ trình chi tiết giống Google Maps
    routingControl = L.Routing.control({
        waypoints: [
            L.latLng(mechLat, mechLon),
            L.latLng(custLat, custLon)
        ],
        routeWhileDragging: false,
        addWaypoints: false,
        // language: 'vi', // Bỏ đi do leaflet-routing-machine có thể không có mặc định 'vi'
        createMarker: function(i, waypoint, n) {
            // Sử dụng marker tùy chỉnh cho điểm đầu và cuối
            const markerIcon = (i === 0) ? mechIcon : custIcon;
            const popupText = (i === 0) ? "Vị trí của bạn" : "Vị trí Khách hàng";
            const marker = L.marker(waypoint.latLng, { icon: markerIcon });
            marker.bindPopup(popupText);
            if(i === 0) marker.openPopup();
            return marker;
        },
        lineOptions: {
            styles: [{ color: '#1989fa', opacity: 0.8, weight: 6 }]
        },
        show: false // Mặc định ẩn UI hiển thị text dẫn đường ở góc để tiết kiệm không gian
    }).addTo(mapInstance);

    // Sửa lỗi hiển thị tile leaflet khi map render trong popup ẩn
    // Đảm bảo chạy sau khi hiệu ứng mở popup hoàn tất hoàn toàn
    setTimeout(() => {
        if (mapInstance) {
            mapInstance.invalidateSize();
            // Khớp lại góc nhìn phòng trường hợp cần thiết
            const group = new L.featureGroup([
               L.marker([mechLat, mechLon]),
               L.marker([custLat, custLon])
            ]);
            mapInstance.fitBounds(group.getBounds(), { padding: [50, 50] });
        }
    }, 500); // Chờ 500ms cho van-popup kết thúc animation
}

const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString('vi-VN');
}

const formatPrice = (p) => {
    return Number(p || 0).toLocaleString('vi-VN') + ' VNĐ';
}

const translateStatus = (s) => {
    const map = { 
        'PENDING': 'Chờ nhận', 
        'ACCEPTED': 'Đã nhận', 
        'ON_THE_WAY': 'Đang đến',
        'IN_PROGRESS': 'Đang sửa',
        'CONFIRMED': 'Đã có lịch', 
        'COMPLETED': 'Xong', 
        'CANCELLED': 'Đã hủy' 
    };
    return map[s] || s;
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

.mechanic-container {
  background: #f3f4f8;
  min-height: 100vh;
  padding-bottom: 70px;
  font-family: 'Inter', sans-serif;
}

/* Ghi đè nav-bar */
:deep(.van-nav-bar) {
  background: linear-gradient(135deg, #1a6fdf, #4f46e5) !important;
}
:deep(.van-nav-bar__title) { color: #fff !important; font-weight: 700; }
:deep(.van-nav-bar .van-icon) { color: #fff !important; }

/* Banner trạng thái khả dụng */
:deep(.van-notice-bar) {
  border-radius: 0;
  font-weight: 600;
  font-size: 13px;
}

/* Thẻ chức năng */
:deep(.van-tabs__wrap) { background: #fff; height: 50px; }

.p-2 { padding: 12px; }
.mt-1 { margin-top: 5px; color: #888; font-size: 12px; }

/* ─── Thẻ đơn SOS / Lịch hẹn ─── */
.order-card {
  background: #fff;
  border-radius: 14px;
  margin-bottom: 10px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.order-header {
  display: flex;
  align-items: center;
  padding: 12px 14px;
  gap: 12px;
  border-bottom: 1px solid #f3f4f8;
}
.order-avatar {
  width: 42px; height: 42px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e0eaff, #c7d7ff);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  color: #2563eb;
  font-size: 18px;
}
.order-meta { flex: 1; min-width: 0; }
.order-title { font-size: 14px; font-weight: 700; color: #1a1a2e; }
.order-sub { font-size: 12px; color: #aaa; margin-top: 2px; }
.order-status-chip {
  font-size: 11px; font-weight: 700;
  padding: 3px 10px; border-radius: 20px;
}
.chip-pending  { background: #fff8e1; color: #b45309; }
.chip-accepted { background: #e0eaff; color: #2563eb; }
.chip-completed { background: #d4fae4; color: #1a7a4a; }
.chip-cancelled { background: #f3f4f8; color: #aaa; }

.order-body { padding: 10px 14px; }
.order-field { font-size: 12px; color: #666; margin-bottom: 4px; }
.order-field strong { color: #333; }

.order-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
  padding: 12px 14px;
  background: #fafafa;
  border-top: 1px solid #f3f4f8;
}

/* ─── Ghi đè cấu hình nút (Modern) ─── */
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
/* Kiểu dáng các nút dạng plain */
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

/* ─── Revenue / Stats ─── */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 14px;
}
.revenue-card {
  background: #fff;
  padding: 16px;
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  text-align: center;
}
.revenue-card h3 { margin: 0 0 8px; color: #aaa; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.revenue-card .price { font-size: 20px; font-weight: 700; color: #2563eb; }
.revenue-card-full { grid-column: 1 / -1; }

.chart-mock { background: #fff; padding: 14px; border-radius: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.chart-mock p { font-size: 12px; color: #aaa; margin-bottom: 10px; font-weight: 600; text-transform: uppercase; }
.bars { display: flex; align-items: flex-end; justify-content: space-around; height: 80px; }
.bar {
  width: 9%; border-radius: 6px 6px 0 0;
  font-size: 9px; display: flex; align-items: flex-end;
  justify-content: center; padding-bottom: 2px;
  color: #fff; font-weight: 700;
  background: linear-gradient(180deg, #4f46e5, #2563eb);
}

.map-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 15px; background: #fff; border-bottom: 1px solid #ebedf0;
}
.map-header .title { font-weight: bold; font-size: 16px; }
.mt-4 { margin-top: 16px; }
.stat-text { text-align: center; font-size: 12px; margin-top: 6px; color: #888; }
.mini-price { font-weight: 700; color: #2563eb; }

/* Stats breakdown */
.stats-section { padding: 0 4px; }
.stats-subtitle { font-size: 13px; font-weight: 700; color: #555; margin: 12px 0 8px; }
.stats-row { display: flex; gap: 10px; }
.stats-mini {
  flex: 1; background: #f8f9fa; border-radius: 12px; padding: 12px;
  text-align: center;
}
.sm-label { font-size: 11px; color: #aaa; font-weight: 600; text-transform: uppercase; }
.sm-count { font-size: 14px; font-weight: 700; color: #333; margin: 4px 0; }
.sm-price { font-size: 12px; font-weight: 700; color: #2563eb; }
.cancelled-stat {
  margin-top: 12px; text-align: center; font-size: 13px; color: #e74c3c;
  font-weight: 600; padding: 8px; background: #fff5f5; border-radius: 10px;
}

/* POPUP CHAT */
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
