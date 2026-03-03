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
        <van-tab title="SOS" name="SOS"></van-tab>
        <van-tab title="Lịch Hẹn" name="APPT"></van-tab>
        <van-tab title="Thống Kê" name="STATS"></van-tab>
    </van-tabs>

    <!-- SOS TAB CONTENT -->
    <div v-if="activeTab === 'SOS'" class="p-2">
         <van-tabs v-model:active="sosSubTab">
            <van-tab title="Mới" name="PENDING"></van-tab>
            <van-tab title="Đang làm" name="ACCEPTED"></van-tab>
         </van-tabs>

         <div v-if="loadingSOS" class="text-center p-4">Đang tải SOS...</div>
         <van-empty v-if="!loadingSOS && filteredSOS.length === 0" description="Không có đơn SOS nào" />
         
         <van-card
            v-for="item in filteredSOS"
            :key="'sos-'+item.id"
            :tag="translateStatus(item.status)"
            :price="item.problem_description"
            desc="Mô tả sự cố:"
            :title="`Khách: #${item.customer}`"
            :thumb="'https://img.freepik.com/free-icon/user_318-159711.jpg'"
        >
            <template #footer>
                <van-button v-if="item.status === 'PENDING'" size="small" type="primary" @click="updateSOSStatus(item.id, 'ACCEPTED')">Nhận Đơn</van-button>
                <div v-if="item.status === 'ACCEPTED'">
                    <van-button size="small" type="warning" plain @click="viewRoute(item)">Chỉ Đường</van-button>
                    <van-button size="small" type="success" @click="updateSOSStatus(item.id, 'COMPLETED')">Hoàn Thành</van-button>
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
            :desc="`Thời gian: ${formatDate(item.appointment_time)}`"
            :title="`Khách: ${item.customer_name || '#' + item.customer}`" 
             thumb="https://img.freepik.com/free-vector/date-picker-concept-illustration_114360-4668.jpg"
        >
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
            
            <div class="chart-mock mt-4">
                <p>Biểu đồ tuần này</p>
                <div class="bars">
                    <div class="bar" style="height: 40%">T2</div>
                    <div class="bar" style="height: 60%">T3</div>
                    <div class="bar" style="height: 30%">T4</div>
                    <div class="bar" style="height: 80%">T5</div>
                    <div class="bar" style="height: 50%">T6</div>
                    <div class="bar" style="height: 90%; background: #1989fa;">CN</div>
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

  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue';
import axios from 'axios';
import { showToast } from 'vant';
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

const fetchSOS = async () => {
    loadingSOS.value = true;
    try {
        const res = await axios.get('/api/bookings/mechanic/list/');
        sosBookings.value = res.data;
    } catch (e) {
        console.error(e);
    } finally {
        loadingSOS.value = false;
    }
}

const fetchAppt = async () => {
    loadingAppt.value = true;
    try {
        const res = await axios.get('/api/services/mechanic/list/');
        appointments.value = res.data;
    } catch (e) {
        console.error(e);
    } finally {
        loadingAppt.value = false;
    }
}

const fetchStats = async () => {
    loadingStats.value = true;
    try {
        const res = await axios.get('/api/services/mechanic/revenue/');
        stats.value = res.data;
    } catch (e) {
        console.error(e);
    } finally {
        loadingStats.value = false;
    }
}

const refreshData = () => {
    if (activeTab.value === 'SOS') fetchSOS();
    else if (activeTab.value === 'APPT') fetchAppt();
    else fetchStats();
}

// Initial load
onMounted(refreshData);

const filteredSOS = computed(() => {
    return sosBookings.value.filter(b => b.status === sosSubTab.value);
});

const updateSOSStatus = async (id, status) => {
    try {
        await axios.post(`/api/bookings/${id}/update-status/`, { status });
        showToast('Cập nhật SOS thành công!');
        fetchSOS();
    } catch (e) {
        showToast('Lỗi cập nhật SOS');
    }
}

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
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(p || 0);
}

const translateStatus = (s) => {
    const map = { 'PENDING': 'Chờ', 'ACCEPTED': 'Đang làm', 'CONFIRMED': 'Đã có lịch', 'COMPLETED': 'Xong', 'CANCELLED': 'Đã hủy' };
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
:deep(.van-tabs__wrap) { background: #fff; }

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
  padding: 10px 14px;
  background: #fafafa;
  border-top: 1px solid #f3f4f8;
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
</style>

