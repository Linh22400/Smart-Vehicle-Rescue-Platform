<template>
  <div class="booking-screen">
    <!-- Map Container -->
    <div id="map" class="map-container"></div>

    <!-- Floating Action Panel -->
    <div class="fab-panel">
      <button class="fab-ai" @click="openAIModal">
        <van-icon name="scan" size="16" />
        Chẩn Đoán AI
      </button>
      <button class="fab-sos" @click="handleSOS" :disabled="loading">
        <van-icon name="phone-o" size="18" />
        <span>{{ loading ? '...' : 'SOS Cứu Hộ' }}</span>
      </button>
    </div>

    <!-- Floating Mechanic Cards (Uber/Grab style) -->
    <transition name="slide-up">
      <div v-if="showMechanics" class="mech-float-panel">
        <!-- Header row -->
        <div class="mfp-header">
          <div class="mfp-title">
            <van-icon name="location-o" color="#2563eb" size="15" />
            <span>{{ mechanics.length }} thợ gần bạn (5km)</span>
          </div>
          <button class="mfp-close" @click="showMechanics = false">
            <van-icon name="cross" size="16" color="#888" />
          </button>
        </div>

        <!-- Horizontal scroll cards -->
        <div class="mfp-scroll">
          <div
            v-for="mech in mechanics"
            :key="mech.id"
            class="mfp-card"
            @click="bookMechanic(mech)"
          >
            <!-- Avatar -->
            <div class="mfp-avatar">
              <van-icon name="manager-o" size="28" color="#fff" />
            </div>

            <!-- Info -->
            <div class="mfp-name">{{ mech.username }}</div>
            <div class="mfp-spec">{{ mech.specialty || 'Đa dịch vụ' }}</div>

            <!-- Stats row -->
            <div class="mfp-stats">
              <div class="mfp-stat">
                <van-icon name="location-o" size="12" color="#2563eb" />
                <span>{{ mech.distance_km }}km</span>
              </div>
              <div class="mfp-stat star">
                <span>&#9733;</span>
                <span>{{ mech.rating }}</span>
              </div>
            </div>

            <!-- CTA -->
            <button class="mfp-btn">Gọi ngay</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- AI Check Popup -->
    <van-popup
      v-model:show="showAIModal"
      position="bottom"
      round
      :style="{ maxHeight: '92%' }"
      closeable
    >
      <div class="ai-wrap">

        <!-- Header -->
        <div class="ai-header">
          <div class="ai-header-icon"><van-icon name="scan" size="26" color="#5c6bc0" /></div>
          <div>
            <div class="ai-header-title">Chẩn Đoán Xe</div>
            <!--<div class="ai-header-sub">Powered by Gemini AI</div>-->
          </div>
        </div>

        <!-- Upload State -->
        <div v-if="!aiResult" class="ai-upload-state">
          <div v-if="!aiLoading">
            <div class="ai-upload-icon"><van-icon name="photograph" size="48" color="#bbb" /></div>
            <p class="ai-upload-title">Chụp ảnh phần hư hỏng</p>
            <p class="ai-upload-desc">AI sẽ phân tích và ước tính chi phí sửa chữa cho bạn</p>
            <van-uploader
              v-model="fileList"
              :max-count="1"
              :after-read="analyzeImage"
              accept="image/*"
            />
          </div>
          <div v-else class="ai-analyzing">
            <div class="ai-spinner"></div>
            <p class="ai-analyzing-text">AI đang phân tích…</p>
            <p class="ai-analyzing-sub">Thường mất 5–15 giây</p>
          </div>
        </div>

        <!-- Result State -->
        <div v-if="aiResult" class="ai-result-wrap">

          <!-- Status Strip -->
          <div class="ai-status-strip" :class="'strip-' + severityKey">
            <div class="ai-status-left">
              <span class="ai-status-dot"></span>
              <span class="ai-status-label">{{ aiResult.severity }}</span>
            </div>
            <div class="ai-drive-chip" :class="aiResult.can_drive ? 'chip-ok' : 'chip-stop'">
              {{ aiResult.can_drive ? '✓ Có thể lái' : '× Không nên lái' }}
            </div>
          </div>

          <!-- Diagnosis Block -->
          <div class="ai-card">
            <div class="ai-section-head">
              <div class="ai-icon-box blue"><van-icon name="description" size="14" color="#fff" /></div>
              <span>Chẩn đoán</span>
            </div>
            <div class="ai-card-value">{{ aiResult.diagnosis }}</div>
            <div v-if="aiResult.root_cause" class="ai-root-cause">
              <van-icon name="question-o" size="12" color="#a0aec0" />
              <span>{{ aiResult.root_cause }}</span>
            </div>
            <div class="ai-divider"></div>
            <div class="ai-section-head">
              <div class="ai-icon-box purple"><van-icon name="notes-o" size="14" color="#fff" /></div>
              <span>Mô tả chi tiết</span>
            </div>
            <div class="ai-card-detail">{{ aiResult.details }}</div>
          </div>

          <!-- Parts Needed -->
          <div v-if="aiResult.parts_needed && aiResult.parts_needed.length > 0" class="ai-parts-wrap">
            <div class="ai-section-head" style="padding: 10px 14px 6px">
              <div class="ai-icon-box green"><van-icon name="setting-o" size="13" color="#fff" /></div>
              <span>Linh kiện có thể cần thay</span>
            </div>
            <div class="ai-parts-list">
              <span v-for="part in aiResult.parts_needed" :key="part" class="ai-part-chip">
                {{ part }}
              </span>
            </div>
          </div>

          <!-- Price Breakdown Table -->
          <div class="ai-price-card">
            <div class="ai-price-header">
              <div class="ai-icon-box indigo"><van-icon name="balance-o" size="13" color="#fff" /></div>
              <span>Bảng giá tham khảo</span>
            </div>

            <!-- Parts cost row -->
            <div class="ai-price-row">
              <div class="apr-left">
                <div class="apr-dot" style="background:#10b981"></div>
                <div class="apr-stack">
                  <span class="apr-label">Linh kiện</span>
                  <span class="apr-range">{{ aiResult.parts_cost || 'Chưa xác định' }}</span>
                </div>
              </div>
              <div v-if="aiResult.parts_recommended" class="apr-recommend green">
                {{ aiResult.parts_recommended }}
              </div>
            </div>

            <!-- Labor cost row -->
            <div class="ai-price-row">
              <div class="apr-left">
                <div class="apr-dot" style="background:#f59e0b"></div>
                <div class="apr-stack">
                  <span class="apr-label">Công thợ</span>
                  <span class="apr-range">{{ aiResult.labor_cost || 'Chưa xác định' }}</span>
                </div>
              </div>
              <div v-if="aiResult.labor_recommended" class="apr-recommend amber">
                {{ aiResult.labor_recommended }}
              </div>
            </div>

            <!-- Total highlight box -->
            <div class="ai-total-box">
              <div class="ai-total-left">
                <div class="ai-total-label">Tổng ước tính</div>
                <div class="ai-total-range">{{ aiResult.estimated_price }}</div>
              </div>
              <div class="ai-total-recommend">
                <div class="ai-total-rec-label">Giá hợp lý</div>
                <div class="ai-total-rec-value">{{ aiResult.total_recommended || '—' }}</div>
              </div>
            </div>

            <div v-if="aiResult.price_note" class="ai-price-note">
              <van-icon name="bulb-o" size="13" color="#b45309" style="flex-shrink:0;margin-top:1px" />
              <span>{{ aiResult.price_note }}</span>
            </div>
          </div>


          <!-- Urgency Bar -->
          <div class="ai-stats-row">
            <div class="ai-stat-box full">
              <div class="ai-stat-label">Mức khẩn cấp</div>
              <div class="ai-urgency-bar">
                <div
                  v-for="i in 5" :key="i"
                  class="ai-urgency-seg"
                  :class="i <= aiResult.urgency_level ? 'seg-' + severityKey : 'seg-off'"
                ></div>
              </div>
            </div>
          </div>

          <!-- Warning Signs -->
          <div v-if="aiResult.warning_signs" class="ai-warning-box">
            <div class="ai-icon-box red" style="flex-shrink:0">
              <van-icon name="fire-o" size="14" color="#fff" />
            </div>
            <div>
              <div class="ai-warn-title">Dấu hiệu nguy hiểm — dừng xe ngay nếu:</div>
              <div class="ai-warn-text">{{ aiResult.warning_signs }}</div>
            </div>
          </div>

          <!-- Recommendation -->
          <div class="ai-recommendation">
            <div class="ai-icon-box slate" style="flex-shrink:0">
              <van-icon name="shield-o" size="14" color="#fff" />
            </div>
            <div class="ai-rec-text">{{ aiResult.recommended_action }}</div>
          </div>

          <!-- Gemini Badge -->
          <div class="ai-powered-row">
            <span class="ai-powered-badge" :class="aiResult.ai_powered ? '' : 'badge-warn'">
              {{ aiResult.ai_powered ? '✨ Kết quả AI Gemini' : '⚠ Kết quả dự phòng' }}
            </span>
          </div>

          <!-- Action Buttons -->
          <div class="ai-btn-row">
            <button class="ai-btn-secondary" @click="resetAI">↺ Phân tích lại</button>
            <button class="ai-btn-danger" @click="callSOSFromAI">Gọi Cứu Hộ Ngay</button>
          </div>


        </div>
      </div>
    </van-popup>
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
const aiLoading = ref(false);

import { computed } from 'vue';

// Computed: severity theming for the banner
const severityKey = computed(() => {
    const map = {
        'Nhẹ': 'low',
        'Trung bình': 'medium',
        'Nghiêm trọng': 'high',
        'Nguy hiểm': 'critical'
    };
    return map[aiResult.value?.severity] || 'low';
});
const severityClass = computed(() => 'sev-' + severityKey.value);
const severityIcon = computed(() => {
    const map = { 'low': '✅', 'medium': '⚠️', 'high': '🔴', 'critical': '🔥' };
    return map[severityKey.value] || 'ℹ️';
});
const canDriveType = computed(() => aiResult.value?.can_drive ? 'success' : 'danger');

const openAIModal = () => {
    aiResult.value = null;
    fileList.value = [];
    showAIModal.value = true;
};

const resetAI = () => {
    aiResult.value = null;
    fileList.value = [];
};

const callSOSFromAI = () => {
    showAIModal.value = false;
    handleSOS();
};

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

// AI Analysis - Gemini Vision
async function analyzeImage(file) {
    const formData = new FormData();
    formData.append('image', file.file);
    
    aiLoading.value = true;
    aiResult.value = null;
    try {
        const res = await axios.post('/api/ai/analyze-damage/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        aiResult.value = res.data;
    } catch (e) {
        showToast('Lỗi kết nối AI server');
        aiResult.value = {
            diagnosis: 'Không thể kết nối AI',
            severity: 'Trung bình',
            details: 'Không thể phân tích ảnh lúc này. Vui lòng mô tả trực tiếp với thợ.',
            estimated_price: 'Liên hệ thợ kiểm tra',
            recommended_action: 'Gọi cứu hộ để được tư vấn trực tiếp',
            can_drive: false,
            urgency_level: 3,
            ai_powered: false
        };
    } finally {
        aiLoading.value = false;
    }
}
</script>

<style scoped>
.map-container {
  height: 100vh;
  width: 100%;
  z-index: 1;
}
/* ─── Floating Action Panel ─── */
.fab-panel {
  position: absolute;
  bottom: 72px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 1000;
  padding: 0 12px;
  width: 100%;
  max-width: 480px;
  box-sizing: border-box;
}

/* SOS – dominant red pill */
.fab-sos {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 50px;
  background: linear-gradient(135deg, #e03131, #c92a2a);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  border: none;
  border-radius: 14px;
  box-shadow: 0 6px 20px rgba(192,41,41,0.45);
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  letter-spacing: 0.3px;
}
.fab-sos:active {
  transform: scale(0.97);
  box-shadow: 0 3px 10px rgba(192,41,41,0.35);
}
.fab-sos:disabled { opacity: 0.7; }

/* AI – compact secondary pill */
.fab-ai {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 50px;
  padding: 0 16px;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(8px);
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
  border: 1.5px solid rgba(37,99,235,0.3);
  border-radius: 14px;
  box-shadow: 0 4px 14px rgba(37,99,235,0.18);
  cursor: pointer;
  transition: transform 0.15s, background 0.15s;
  white-space: nowrap;
}
.fab-ai:active {
  transform: scale(0.97);
  background: rgba(224,234,255,0.96);
}

.p-4 { padding: 16px; }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 16px; }
.ml-2 { margin-left: 8px; }


/* ===== AI MODAL – Clean Design ===== */
.ai-wrap {
  padding-bottom: 28px;
  overflow-y: auto;
  background: #f5f6f8;
  border-radius: 20px 20px 0 0;
}

/* Header */
.ai-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 20px 14px;
  background: #fff;
  border-bottom: 1px solid #ebebeb;
}
.ai-header-icon { font-size: 28px; line-height: 1; }
.ai-header-title { font-size: 17px; font-weight: 700; color: #1a1a1a; }
.ai-header-sub { font-size: 12px; color: #999; margin-top: 1px; }

/* Upload state */
.ai-upload-state {
  padding: 32px 24px;
  background: #fff;
  text-align: center;
}
.ai-upload-icon { font-size: 48px; margin-bottom: 12px; }
.ai-upload-title { font-size: 16px; font-weight: 600; color: #222; margin: 0 0 6px; }
.ai-upload-desc { font-size: 13px; color: #888; margin: 0 0 20px; line-height: 1.5; }

/* Analyzing spinner */
.ai-analyzing { padding: 20px; text-align: center; }
.ai-spinner {
  width: 44px; height: 44px;
  border: 4px solid #e8eaf6;
  border-top-color: #5c6bc0;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 14px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.ai-analyzing-text { font-size: 16px; font-weight: 600; color: #333; margin: 0 0 4px; }
.ai-analyzing-sub { font-size: 12px; color: #aaa; margin: 0; }

/* ===== Result section ===== */
.ai-result-wrap { padding: 12px 14px 4px; }

/* Status strip – thin colored bar */
.ai-status-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-radius: 10px;
  margin-bottom: 12px;
  border-left: 5px solid;
}
.strip-low    { background: #edfcf4; border-color: #1db954; }
.strip-medium { background: #fffaeb; border-color: #f5a623; }
.strip-high   { background: #fff2f2; border-color: #e03131; }
.strip-critical { background: #ffeaea; border-color: #c0392b; }

.ai-status-left { display: flex; align-items: center; gap: 8px; }
.ai-status-dot {
  width: 10px; height: 10px; border-radius: 50%;
  display: inline-block;
}
.strip-low .ai-status-dot    { background: #1db954; }
.strip-medium .ai-status-dot { background: #f5a623; }
.strip-high .ai-status-dot   { background: #e03131; }
.strip-critical .ai-status-dot { background: #c0392b; animation: blink 0.9s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

.ai-status-label {
  font-size: 14px;
  font-weight: 700;
  color: #222;
}
.strip-low .ai-status-label    { color: #1db954; }
.strip-medium .ai-status-label { color: #e08800; }
.strip-high .ai-status-label   { color: #e03131; }
.strip-critical .ai-status-label { color: #c0392b; }

/* Drive chip */
.ai-drive-chip {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}
.chip-ok   { background: #d4fae4; color: #1a7a4a; }
.chip-stop { background: #ffe0e0; color: #c0392b; }

/* Main card */
.ai-card {
  background: #fff;
  border-radius: 14px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  margin-bottom: 10px;
}
.ai-card-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #aaa;
  font-weight: 600;
  margin-bottom: 5px;
}
.ai-card-value {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.4;
  margin-bottom: 14px;
}
.ai-divider { height: 1px; background: #f0f0f0; margin: 0 -16px 14px; }
.ai-card-detail {
  font-size: 13px;
  color: #555;
  line-height: 1.7;
}

/* Stats row */
.ai-stats-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}
.ai-stat-box {
  flex: 1;
  background: #fff;
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.ai-stat-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: #bbb;
  font-weight: 600;
  margin-bottom: 8px;
}
.ai-stat-value.price {
  font-size: 14px;
  font-weight: 700;
  color: #2d6cdf;
  line-height: 1.3;
}

/* Urgency bar */
.ai-urgency-bar { display: flex; gap: 4px; align-items: center; }
.ai-urgency-seg {
  flex: 1; height: 6px; border-radius: 3px;
}
.seg-off { background: #ebebeb; }
.seg-low      { background: #1db954; }
.seg-medium   { background: #f5a623; }
.seg-high     { background: #e03131; }
.seg-critical { background: #c0392b; }

/* Recommendation */
.ai-recommendation {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #fff;
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.ai-rec-icon { font-size: 20px; flex-shrink: 0; margin-top: 1px; }
.ai-rec-text { font-size: 13px; color: #333; line-height: 1.6; font-weight: 500; }

/* Powered row */
.ai-powered-row { text-align: center; margin-bottom: 14px; }
.ai-powered-badge {
  font-size: 11px;
  color: #888;
  background: #f0f0f0;
  border-radius: 20px;
  padding: 3px 12px;
}
.badge-warn { background: #fff8e1; color: #e08800; }

/* Action buttons – custom native for full control */
.ai-btn-row {
  display: flex;
  gap: 10px;
  padding: 4px 2px 8px;
}
.ai-btn-secondary {
  flex: 1;
  height: 46px;
  border: 1.5px solid #d0d0d0;
  background: #fff;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #555;
  cursor: pointer;
  transition: background 0.15s;
}
.ai-btn-secondary:active { background: #f5f5f5; }
.ai-btn-danger {
  flex: 1.6;
  height: 46px;
  border: none;
  background: linear-gradient(135deg, #e03131, #c0392b);
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(192,57,43,0.3);
  transition: transform 0.1s, box-shadow 0.1s;
}
.ai-btn-danger:active { transform: scale(0.97); box-shadow: none; }

.ai-modal-header {
  padding: 16px;
  font-size: 16px;
  font-weight: bold;
  color: #333;
  border-bottom: 1px solid #ebedf0;
  background: #f7f8fa;
  text-align: center;
}
.ai-upload-area {
  padding: 20px;
  text-align: center;
}
.ai-hint {
  color: #666;
  font-size: 14px;
  margin-bottom: 16px;
}
.ai-loading {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #1989fa;
  font-size: 14px;
}

/* Result Card */
.ai-result {
  padding: 12px;
}
.ai-severity-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 12px;
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 12px;
}
.sev-low { background: #f0fff8; color: #07c160; border: 1px solid #07c160; }
.sev-medium { background: #fffbe8; color: #ed6a0c; border: 1px solid #ed6a0c; }
.sev-high { background: #fff2f0; color: #ee0a24; border: 1px solid #ee0a24; }
.sev-critical { background: #1a0000; color: #ff4444; border: 1px solid #ff4444; animation: pulse 1s infinite; }
.severity-icon { font-size: 20px; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.ai-diagnosis-card {
  background: #fff;
  border-radius: 10px;
  padding: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 4px;
}
.ai-diagnosis-card h3 { margin: 0 0 8px 0; font-size: 14px; color: #323233; }
.ai-diagnosis-card h4 { margin: 10px 0 6px 0; font-size: 13px; color: #666; }
.diagnosis-text { font-size: 15px; font-weight: 600; color: #333; margin: 0; }
.details-text { font-size: 13px; color: #555; line-height: 1.6; margin: 0; }

/* Urgency Dots */
.urgency-dots { display: flex; gap: 4px; align-items: center; }
.dot {
  width: 12px; height: 12px; border-radius: 50%;
  background: #ebedf0;
}
.dot.active { background: #ee0a24; }

/* AI Badge */
.ai-badge { padding: 10px 12px; text-align: right; }

/* Action Buttons */
.ai-actions {
  display: flex;
  gap: 10px;
  padding: 12px;
  justify-content: space-between;
}
.ai-actions .van-button { flex: 1; }

/* ─── Mechanic Picker Drawer ─── */
.mechanic-drawer {
  padding: 12px 12px 28px;
  max-height: 60vh;
  overflow-y: auto;
}

/* Grid layout */
.mech-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.mech-grid-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px 10px 12px;
  box-shadow: 0 3px 12px rgba(0,0,0,0.10);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  border: 1.5px solid #f0f0f0;
}
.mech-grid-card:active {
  transform: scale(0.96);
  box-shadow: 0 1px 5px rgba(0,0,0,0.07);
}

/* Avatar circle */
.mgc-avatar {
  width: 48px; height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 8px;
  box-shadow: 0 3px 10px rgba(37,99,235,0.3);
}

.mgc-name {
  font-size: 14px;
  font-weight: 800;
  color: #111;
  margin-bottom: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  letter-spacing: -0.2px;
}
.mgc-spec {
  font-size: 12px;
  font-weight: 600;
  color: #555;
  margin-bottom: 7px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
.mgc-meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #555;
  margin-bottom: 10px;
  align-items: center;
  justify-content: center;
}
.mgc-dist { display: flex; align-items: center; gap: 2px; }
.mgc-star  { color: #e67e00; font-weight: 800; font-size: 13px; }

.mgc-btn {
  width: 100%;
  height: 34px;
  background: linear-gradient(90deg, #2563eb, #4f46e5);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  transition: opacity 0.15s;
  letter-spacing: 0.3px;
}
.mgc-btn:active { opacity: 0.85; }


/* ═══════════════════════════════════════
   FLOATING MECHANIC PANEL (Uber/Grab style)
   ═══════════════════════════════════════ */
.mech-float-panel {
  position: absolute;
  bottom: 134px;          /* sits above the FAB panel */
  left: 0; right: 0;
  z-index: 999;
  padding: 0 12px;
}

/* ─── header ─── */
.mfp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255,255,255,0.96);
  backdrop-filter: blur(10px);
  border-radius: 14px 14px 0 0;
  padding: 10px 14px;
  border-bottom: 1px solid #eef0f5;
}
.mfp-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
  color: #1a1a2e;
}
.mfp-close {
  background: #f3f4f8;
  border: none;
  border-radius: 50%;
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
}

/* ─── horizontal scroll strip ─── */
.mfp-scroll {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 12px 14px 16px;
  background: rgba(255,255,255,0.96);
  backdrop-filter: blur(10px);
  border-radius: 0 0 16px 16px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.mfp-scroll::-webkit-scrollbar { display: none; }

/* ─── individual mechanic card ─── */
.mfp-card {
  flex: 0 0 140px;
  background: #fff;
  border-radius: 16px;
  padding: 16px 12px 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.10);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  border: 1.5px solid #eef0f5;
  transition: transform 0.15s, box-shadow 0.15s;
}
.mfp-card:active {
  transform: scale(0.96);
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

/* Avatar */
.mfp-avatar {
  width: 56px; height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(37,99,235,0.35);
  margin-bottom: 10px;
}

/* Name */
.mfp-name {
  font-size: 14px;
  font-weight: 800;
  color: #111;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 116px;
  margin-bottom: 3px;
}

/* Specialty */
.mfp-spec {
  font-size: 11px;
  font-weight: 600;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 116px;
  margin-bottom: 8px;
}

/* Stats row */
.mfp-stats {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  justify-content: center;
}
.mfp-stat {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  font-weight: 700;
  color: #444;
  background: #f3f4f8;
  padding: 3px 7px;
  border-radius: 20px;
}
.mfp-stat.star { background: #fff8e1; color: #e67e00; }

/* CTA button */
.mfp-btn {
  width: 100%;
  height: 36px;
  background: linear-gradient(90deg, #e03131, #c92a2a);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 3px 10px rgba(192,41,41,0.3);
  transition: opacity 0.15s;
  letter-spacing: 0.3px;
}
.mfp-btn:active { opacity: 0.85; }

/* ─── Slide-up transition ─── */
.slide-up-enter-active {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease;
}
.slide-up-leave-active {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.slide-up-enter-from { transform: translateY(40px); opacity: 0; }
.slide-up-leave-to  { transform: translateY(40px); opacity: 0; }


/* ─── Icon Box System ─── */
.ai-icon-box {
  width: 26px; height: 26px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.ai-icon-box.blue   { background: linear-gradient(135deg, #2563eb, #3b82f6); }
.ai-icon-box.purple { background: linear-gradient(135deg, #7c3aed, #a78bfa); }
.ai-icon-box.green  { background: linear-gradient(135deg, #059669, #34d399); }
.ai-icon-box.indigo { background: linear-gradient(135deg, #4f46e5, #818cf8); }
.ai-icon-box.red    { background: linear-gradient(135deg, #e03131, #fc8181); }
.ai-icon-box.slate  { background: linear-gradient(135deg, #475569, #94a3b8); }

/* Section head (icon + label row) */
.ai-section-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px 6px;
  font-size: 12px;
  font-weight: 700;
  color: #444;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Price row with dot indicator */
.apr-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.apr-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Root cause */
.ai-root-cause {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #a0aec0;
  margin-top: 5px;
  font-style: italic;
  padding: 0 14px;
}

/* Parts chips */
.ai-parts-wrap { background: #fff; border-radius: 12px; margin: 0 12px 8px; }
.ai-parts-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 0 14px 12px;
}
.ai-part-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #e0eaff;
  color: #2563eb;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
}

/* Price Breakdown Card */
.ai-price-card {
  background: #fff;
  border-radius: 12px;
  margin: 0 12px 8px;
  overflow: hidden;
  border: 1.5px solid #e0eaff;
}
.ai-price-header {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 10px 14px;
  background: #f0f4ff;
  font-size: 13px;
  font-weight: 700;
  color: #2563eb;
  border-bottom: 1px solid #e0eaff;
}
.ai-price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 9px 14px;
  border-bottom: 1px solid #f5f6f8;
  font-size: 13px;
}
.ai-price-row.total {
  background: #f8faff;
  border-bottom: none;
}
.apr-label { color: #444; font-weight: 700; font-size: 13px; }
.apr-range  { font-size: 11px; color: #999; margin-top: 1px; }

/* Stacked label + range */
.apr-stack { display: flex; flex-direction: column; }

/* Recommended price badge */
.apr-recommend {
  font-size: 12px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 10px;
  white-space: nowrap;
}
.apr-recommend.green  { background: #d1fae5; color: #065f46; }
.apr-recommend.amber  { background: #fef3c7; color: #92400e; }

/* Total highlight box */
.ai-total-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  background: linear-gradient(135deg, #eff6ff, #eef2ff);
  border-top: 1.5px solid #c7d7ff;
}
.ai-total-label { font-size: 11px; font-weight: 600; color: #6b7280; margin-bottom: 3px; }
.ai-total-range { font-size: 12px; color: #6b7280; }
.ai-total-recommend {
  text-align: right;
}
.ai-total-rec-label {
  font-size: 11px;
  color: #2563eb;
  font-weight: 600;
  margin-bottom: 3px;
}
.ai-total-rec-value {
  font-size: 18px;
  font-weight: 800;
  color: #e03131;
  letter-spacing: -0.5px;
}

.ai-price-note {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 8px 14px;
  background: #fffbeb;
  border-top: 1px solid #fde68a;
  font-size: 11px;
  color: #92400e;
  line-height: 1.5;
}

/* Warning Box */
.ai-warning-box {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #fff5f5;
  border: 1.5px solid #fca5a5;
  border-radius: 12px;
  padding: 12px 14px;
  margin: 0 12px 8px;
}
.ai-warn-title { font-size: 12px; font-weight: 700; color: #e03131; margin-bottom: 3px; }
.ai-warn-text  { font-size: 12px; color: #c92a2a; line-height: 1.5; }

/* Full-width urgency stat box */
.ai-stat-box.full { width: 100%; }

</style>



