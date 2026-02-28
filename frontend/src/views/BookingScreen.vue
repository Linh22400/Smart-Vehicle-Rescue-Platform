<template>
  <div class="booking-screen">
    <!-- Map Container -->
    <div id="map" class="map-container"></div>

    <!-- SOS Floating Button -->
    <div class="sos-button-container">
      <van-button type="danger" round size="large" @click="handleSOS" :loading="loading">
        SOS - GỌI CỨU HỘ
      </van-button>
      <van-button type="primary" round size="large" class="mt-2" @click="showAIModal = true">
        Check Hư Hỏng (AI)
      </van-button>
    </div>

    <!-- Found Mechanics Drawer -->
    <van-action-sheet v-model:show="showMechanics" title="Thợ Gần Bạn (5km)">
      <div class="mechanic-list">
        <van-cell-group>
          <van-cell 
            v-for="mech in mechanics" 
            :key="mech.id"
            :title="mech.username" 
            :label="`${mech.specialty} - ${mech.distance_km} km`"
            :value="mech.rating + ' ⭐'"
            is-link
            @click="bookMechanic(mech)"
          />
        </van-cell-group>
        <div v-if="mechanics.length === 0" class="p-4 text-center">
            Không tìm thấy thợ nào gần đây.
        </div>
      </div>
    </van-action-sheet>

    <!-- AI Check Popup -->
    <van-dialog v-model:show="showAIModal" title="Chẩn đoán lỗi bằng AI" show-cancel-button :show-confirm-button="false">
      <div class="p-4">
        <van-uploader v-model="fileList" :max-count="1" :after-read="analyzeImage" />
        <div v-if="aiResult" class="mt-4">
          <p><strong>Chẩn đoán:</strong> {{ aiResult.diagnosis }}</p>
          <p><strong>Giá dự kiến:</strong> {{ aiResult.estimated_price }}</p>
        </div>
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { showToast, showSuccessToast } from 'vant';
import L from 'leaflet';

// State
const router = useRouter();
const map = ref(null);
const userLat = ref(null);
const userLon = ref(null);
const userMarker = ref(null);

// Configure Axios Global
axios.defaults.withCredentials = true;
axios.defaults.baseURL = 'http://localhost:8000'; 

const mechanics = ref([]);
const showMechanics = ref(false);
const loading = ref(false);
let mechanicMarkers = null; // LayerGroup for easy clearing

const showAIModal = ref(false);
const fileList = ref([]);
const aiResult = ref(null);

// Initialize Map
onMounted(() => {
  // Init map with default Hanoi coords
  const defaultLat = 21.0285;
  const defaultLon = 105.8542;
  
  initMap(defaultLat, defaultLon);

  // Try real GPS
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      pos => {
        updateUserLocation(pos.coords.latitude, pos.coords.longitude);
        map.value.setView([pos.coords.latitude, pos.coords.longitude], 15);
      },
      err => {
        showToast('Không lấy được GPS, vui lòng chọn vị trí trên bản đồ');
        updateUserLocation(defaultLat, defaultLon); // Fallback to default
      }
    );
  } else {
    updateUserLocation(defaultLat, defaultLon);
  }
});

function initMap(lat, lon) {
  map.value = L.map('map').setView([lat, lon], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
  }).addTo(map.value);

  // Click on map to set location
  map.value.on('click', (e) => {
    updateUserLocation(e.latlng.lat, e.latlng.lng);
  });
  // Init mechanic markers layer group
  mechanicMarkers = L.layerGroup().addTo(map.value);
}

function updateUserLocation(lat, lon) {
  userLat.value = lat;
  userLon.value = lon;

  if (userMarker.value) {
    userMarker.value.setLatLng([lat, lon]);
  } else {
    // Create Red Marker for User
    const redIcon = new L.Icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });

    userMarker.value = L.marker([lat, lon], { 
      icon: redIcon,
      draggable: true 
    }).addTo(map.value)
      .bindPopup('Vị trí của bạn (Kéo hoặc Click để sửa)')
      .openPopup();

    // Drag event
    userMarker.value.on('dragend', function (e) {
      const coord = e.target.getLatLng();
      userLat.value = coord.lat;
      userLon.value = coord.lng;
    });
  }
}

// SOS Function
async function handleSOS() {
  if (!userLat.value) {
    showToast('Vui lòng chọn vị trí của bạn trên bản đồ');
    return;
  }

  loading.value = true;
  try {
    const response = await axios.post('/api/bookings/sos/', {
      latitude: userLat.value,
      longitude: userLon.value
    });
    mechanics.value = response.data;
    showMechanics.value = true;
    
    // Clear previous mechanic markers before adding new
    if (mechanicMarkers) mechanicMarkers.clearLayers();
    mechanics.value.forEach(m => {
        L.marker([m.latitude, m.longitude]).addTo(mechanicMarkers)
         .bindPopup(`<b>${m.username}</b><br>${m.specialty}<br>${m.distance_km}km`);
    });

  } catch (error) {
    if (error.response && error.response.status === 403) {
         showToast('Lỗi quyền truy cập. Hãy đăng nhập Admin trước!');
    } else {
         showToast('Lỗi kết nối Server');
    }
    console.error(error);
  } finally {
    loading.value = false;
  }
}

async function bookMechanic(mech) {
    try {
        await axios.post('/api/bookings/create/', {
            mechanic: mech.id,
            customer_lat: userLat.value,
            customer_lon: userLon.value,
            problem_description: 'SOS Request via App'
        });
        showSuccessToast(`Đã gửi yêu cầu đến ${mech.username}!`);
        showMechanics.value = false;
        router.push('/history');
    } catch (error) {
        showToast('Lỗi đặt thợ. Vui lòng thử lại.');
        console.error(error);
    }
}

// AI Analysis
async function analyzeImage(file) {
    const formData = new FormData();
    formData.append('image', file.file);
    
    showToast('Đang phân tích...');
    try {
        const res = await axios.post('/api/ai/analyze-damage/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        aiResult.value = res.data;
    } catch (e) {
        showToast('Lỗi AI Server');
    }
}
</script>

<style scoped>
.map-container {
  height: 100vh;
  width: 100%;
  z-index: 1;
}
.sos-button-container {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}
.p-4 { padding: 16px; }
.mt-2 { margin-top: 8px; }
.mt-4 { margin-top: 16px; }
</style>
