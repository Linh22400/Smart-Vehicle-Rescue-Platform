<template>
  <div class="mechanic-container">
    <van-nav-bar title="Dashboard Thợ">
      <template #right>
        <van-icon name="setting-o" size="20" @click="$router.push('/mechanic/profile')" />
      </template>
    </van-nav-bar>

    <!-- Availability Banner -->
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

    <!-- SOS TAB CONTENT -->
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
                    <van-button size="small" type="warning" plain @click="viewRoute(item)">Chỉ Đường</van-button>
                    <van-button size="small" type="primary" @click="updateSOSStatus(item.id, 'ON_THE_WAY')">Bắt Đầu Đi</van-button>
                </div>
                <div v-if="item.status === 'ON_THE_WAY'">
                    <van-button size="small" type="primary" plain icon="chat-o" @click="openChat(item)" style="margin-right:4px">Chat</van-button>
                    <van-button size="small" type="warning" plain @click="viewRoute(item)">Chỉ Đường</van-button>
                    <van-button size="small" type="primary" @click="updateSOSStatus(item.id, 'IN_PROGRESS')">Đã Tới/Đang Sửa</van-button>
                </div>
                <div v-if="item.status === 'IN_PROGRESS'">
                    <van-button size="small" type="primary" plain icon="chat-o" @click="openChat(item)" style="margin-right:4px">Chat</van-button>
                    <van-button size="small" type="success" @click="openCostDialog(item)">Hoàn Thành & Tính Tiền</van-button>
                </div>
            </template>
        </van-card>
    </div>

    <!-- APPOINTMENT TAB CONTENT -->
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
                     <van-button size="small" type="success" @click="updateApptStatus(item.id, 'COMPLETED')">Hoàn Thành</van-button>
                     <van-button size="small" type="danger" @click="updateApptStatus(item.id, 'CANCELLED')">Hủy</van-button>
                </div>
            </template>
        </van-card>
    </div>

    <!-- PAYMENT TAB CONTENT -->
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
                <van-button size="small" type="success" @click="verifyPayment(item)">Xác nhận Đã Nhận Tiền</van-button>
            </template>
        </van-card>
    </div>

    <!-- STATS TAB CONTENT -->
    <div v-if="activeTab === 'STATS'" class="p-2">
        <div v-if="loadingStats" class="text-center p-4">Đang tính toán...</div>
        <div v-else>
            <div class="revenue-card total">
                <h3>Tổng Doanh Thu</h3>
                <div class="price">{{ formatPrice(stats.total_revenue) }}</div>
            </div>

            <van-grid :column-num="2" class="mt-2">
                <van-grid-item icon="gold-coin-o" text="SOS" >
                    <template #icon>
                        <van-icon name="warning-o" color="#ff976a" size="24" />
                    </template>
                    <div class="stat-text">
                        <div>{{ stats.sos_stats?.count || 0 }} đơn</div>
                        <div class="mini-price">{{ formatPrice(stats.sos_stats?.revenue) }}</div>
                    </div>
                </van-grid-item>
                <van-grid-item icon="shop-o" text="Bảo Dưỡng">
                     <template #icon>
                        <van-icon name="shop-o" color="#1989fa" size="24" />
                    </template>
                     <div class="stat-text">
                        <div>{{ stats.service_stats?.count || 0 }} đơn</div>
                        <div class="mini-price">{{ formatPrice(stats.service_stats?.revenue) }}</div>
                    </div>
                </van-grid-item>
            </van-grid>

            <!-- Weekly / Monthly breakdown -->
            <div class="stats-section mt-3">
                <h4 class="stats-subtitle">📅 Tuần này</h4>
                <div class="stats-row">
                    <div class="stats-mini">
                        <div class="sm-label">SOS</div>
                        <div class="sm-count">{{ stats.sos_stats?.week?.count || 0 }} đơn</div>
                        <div class="sm-price">{{ formatPrice(stats.sos_stats?.week?.revenue) }}</div>
                    </div>
                    <div class="stats-mini">
                        <div class="sm-label">Bảo dưỡng</div>
                        <div class="sm-count">{{ stats.service_stats?.week?.count || 0 }} đơn</div>
                        <div class="sm-price">{{ formatPrice(stats.service_stats?.week?.revenue) }}</div>
                    </div>
                </div>

                <h4 class="stats-subtitle">📆 Tháng này</h4>
                <div class="stats-row">
                    <div class="stats-mini">
                        <div class="sm-label">SOS</div>
                        <div class="sm-count">{{ stats.sos_stats?.month?.count || 0 }} đơn</div>
                        <div class="sm-price">{{ formatPrice(stats.sos_stats?.month?.revenue) }}</div>
                    </div>
                    <div class="stats-mini">
                        <div class="sm-label">Bảo dưỡng</div>
                        <div class="sm-count">{{ stats.service_stats?.month?.count || 0 }} đơn</div>
                        <div class="sm-price">{{ formatPrice(stats.service_stats?.month?.revenue) }}</div>
                    </div>
                </div>

                <div v-if="stats.cancelled > 0" class="cancelled-stat" style="display:flex;align-items:center;justify-content:center;gap:4px">
                    <van-icon name="close" color="#ee0a24" /> {{ stats.cancelled }} đơn đã hủy
                </div>
            </div>
        </div>
    </div>

    <!-- MAP ROUTING DIALOG -->
    <van-popup v-model:show="showMap" position="bottom" :style="{ height: '80%' }" @opened="initMap">
        <div class="map-header">
            <span class="title">Bản Đồ Chỉ Đường</span>
            <van-icon name="cross" size="20" @click="showMap = false" />
        </div>
        <div id="mechanic-map" style="width: 100%; height: calc(100% - 40px);"></div>
    </van-popup>

    <!-- REPAIR COST DIALOG -->
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

    <!-- CHAT POPUP -->
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

// Availability state
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
        // Update localStorage
        const userStr = localStorage.getItem('user');
        if (userStr) {
            const user = JSON.parse(userStr);
            if (user.mechanic_profile) user.mechanic_profile.is_available = val;
            localStorage.setItem('user', JSON.stringify(user));
        }
        showToast(val ? 'Đã bật nhận đơn' : 'Đã tắt nhận đơn');
    } catch(e) {
        showToast('Lỗi cập nhật trạng thái');
        isAvailable.value = !val; // revert
    }
}

// Map State
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

// Initial load + auto-poll for new SOS orders
let sosAutoRefresh = null;

const pendingCount = computed(() => {
    return sosBookings.value.filter(b => b.status === 'PENDING').length;
});

onMounted(() => {
    refreshData();
    // Request Browser Notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    // Auto-refresh SOS every 15 seconds for incoming orders
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

const updateSOSStatus = async (id, newStatus) => {
    try {
        await axios.post(`/api/bookings/${id}/update-status/`, { status: newStatus });
        showToast('Cập nhật SOS thành công!');
        // Start GPS sender when mechanic is ON_THE_WAY or IN_PROGRESS
        if (newStatus === 'ON_THE_WAY' || newStatus === 'IN_PROGRESS') {
            startGPSSender();
        }
        // Stop GPS sender when booking is completed or cancelled
        if (newStatus === 'COMPLETED' || newStatus === 'CANCELLED') {
            stopGPSSender();
        }
        fetchSOS();
    } catch (e) {
        showToast('Lỗi cập nhật SOS');
    }
}

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

const previewImage = (url) => {
    if (!url) return;
    showImagePreview([url]);
};

// ── Repair Cost Dialog ──
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
// ── GPS Real-time Location Sender ──
let gpsWatchId = null;
let gpsSendInterval = null;
const currentGPS = ref({ lat: null, lon: null });

const startGPSSender = () => {
    if (gpsSendInterval) return; // already running

    // Watch position using HTML5 Geolocation
    if (navigator.geolocation) {
        gpsWatchId = navigator.geolocation.watchPosition(
            (pos) => {
                currentGPS.value.lat = pos.coords.latitude;
                currentGPS.value.lon = pos.coords.longitude;
            },
            (err) => {
                console.warn('GPS error:', err.message);
            },
            { enableHighAccuracy: true, maximumAge: 5000 }
        );
    }

    // Send location to server every 10 seconds
    gpsSendInterval = setInterval(async () => {
        if (currentGPS.value.lat && currentGPS.value.lon) {
            try {
                await axios.post('/api/users/mechanic/update-location/', {
                    latitude: currentGPS.value.lat,
                    longitude: currentGPS.value.lon
                });
            } catch (e) {
                // Silent fail - don't interrupt mechanic
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

// MAP ROUTING LOGIC
const viewRoute = (item) => {
    activeRouteItem.value = item;
    showMap.value = true;
}

const initMap = async () => {
    if (!mapInstance) {
        mapInstance = L.map('mechanic-map');
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(mapInstance);
    }

    // Clear previous routing controls and layers
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

    // Get Mechanic's current location from user's profile
    const userStr = localStorage.getItem('user');
    
    // Parse floats properly
    const custLat = parseFloat(item.customer_lat);
    const custLon = parseFloat(item.customer_lon);

    // Mock slightly offset mechanic coord
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

    // Use leaflet-routing-machine for detailed routing like Google Maps
    routingControl = L.Routing.control({
        waypoints: [
            L.latLng(mechLat, mechLon),
            L.latLng(custLat, custLon)
        ],
        routeWhileDragging: false,
        addWaypoints: false,
        // language: 'vi', // Removed because leaflet-routing-machine might not have 'vi' built-in without extra files
        createMarker: function(i, waypoint, n) {
            // Use custom markers for start and end
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
        show: false // Hide turn-by-turn text UI by default to save space
    }).addTo(mapInstance);

    // Resize map when shown in popup to fix leaflet tile loading issue
    // Ensure this runs after the popup animation has completely finished
    setTimeout(() => {
        if (mapInstance) {
            mapInstance.invalidateSize();
            // Refit bounds just in case
            const group = new L.featureGroup([
               L.marker([mechLat, mechLon]),
               L.marker([custLat, custLon])
            ]);
            mapInstance.fitBounds(group.getBounds(), { padding: [50, 50] });
        }
    }, 500); // 500ms delay to allow van-popup to finish animating
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

/* Override nav-bar */
:deep(.van-nav-bar) {
  background: linear-gradient(135deg, #1a6fdf, #4f46e5) !important;
}
:deep(.van-nav-bar__title) { color: #fff !important; font-weight: 700; }
:deep(.van-nav-bar .van-icon) { color: #fff !important; }

/* Availability banner */
:deep(.van-notice-bar) {
  border-radius: 0;
  font-weight: 600;
  font-size: 13px;
}

/* Tabs */
:deep(.van-tabs__wrap) { background: #fff; height: 50px; }

.p-2 { padding: 12px; }
.mt-1 { margin-top: 5px; color: #888; font-size: 12px; }

/* ─── SOS / Appt order card ─── */
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
