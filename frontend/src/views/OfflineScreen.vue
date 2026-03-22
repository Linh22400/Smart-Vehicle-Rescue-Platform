<template>
  <div class="offline-page">
    <!-- Ảnh nền động -->
    <div class="offline-bg">
      <div class="pulse-ring pulse-1"></div>
      <div class="pulse-ring pulse-2"></div>
      <div class="pulse-ring pulse-3"></div>
    </div>

    <!-- Khối đầu -->
    <div class="offline-header">
      <div class="offline-icon-wrap">
        <WifiOff :size="36" class="offline-wifi-icon" />
      </div>
      <h1 class="offline-title">Mất Kết Nối</h1>
      <p class="offline-sub">Không có internet — nhưng chúng tôi vẫn ở đây giúp bạn</p>
      <div class="offline-badge">
        <span class="badge-dot"></span> Đang offline
      </div>
    </div>

    <!-- Khối vị trí GPS -->
    <div class="ofc-section">
      <div class="ofc-card gps-card">
        <div class="ofc-card-header">
          <MapPin :size="16" class="ofc-hicon" style="color:#2563eb" />
          <span>Vị trí của bạn</span>
        </div>
        <div v-if="gpsLoading" class="gps-loading">
          <div class="gps-spinner"></div>
          <span>Đang xác định vị trí GPS...</span>
        </div>
        <div v-else-if="gpsError" class="gps-error">
          <AlertTriangle :size="14" style="color:#f59e0b;margin-right:4px;" />
          {{ gpsError }}
        </div>
        <div v-else class="gps-coords">
          <div class="coord-row">
            <span class="coord-label">Vĩ độ</span>
            <span class="coord-value">{{ lat.toFixed(6) }}°</span>
          </div>
          <div class="coord-row">
            <span class="coord-label">Kinh độ</span>
            <span class="coord-value">{{ lon.toFixed(6) }}°</span>
          </div>
          <button class="copy-btn" @click="copyCoords">
            <Copy :size="12" /> Sao chép tọa độ
          </button>
          <p class="gps-hint">Đọc tọa độ này cho thợ qua điện thoại</p>
        </div>
      </div>
    </div>

    <!-- Khối Thợ gần nhất -->
    <div class="ofc-section" v-if="lastMechanic">
      <div class="ofc-label">Thợ gần nhất bạn đã dùng</div>
      <div class="ofc-card mechanic-card">
        <div class="mech-avatar">{{ lastMechanic.name?.charAt(0) || '?' }}</div>
        <div class="mech-info">
          <div class="mech-name">{{ lastMechanic.name }}</div>
          <div class="mech-spec">{{ lastMechanic.specialization || 'Thợ cứu hộ' }}</div>
          <div class="mech-rating" v-if="lastMechanic.rating">
            ⭐ {{ lastMechanic.rating }} điểm
          </div>
        </div>
        <a v-if="lastMechanic.phone" :href="'tel:' + lastMechanic.phone" class="call-btn">
          <Phone :size="16" />
          Gọi
        </a>
      </div>
    </div>

    <!-- Danh bạ khẩn cấp -->
    <div class="ofc-section">
      <div class="ofc-label">Số khẩn cấp</div>
      <div class="emergency-grid">
        <a href="tel:113" class="emr-card police">
          <ShieldAlert :size="22" class="emr-icon" />
          <span class="emr-num">113</span>
          <span class="emr-name">Công an</span>
        </a>
        <a href="tel:114" class="emr-card fire">
          <Flame :size="22" class="emr-icon" />
          <span class="emr-num">114</span>
          <span class="emr-name">Cứu hỏa</span>
        </a>
        <a href="tel:115" class="emr-card medical">
          <Cross :size="22" class="emr-icon" />
          <span class="emr-num">115</span>
          <span class="emr-name">Cấp cứu</span>
        </a>
        <a href="tel:1800599920" class="emr-card towing">
          <Truck :size="22" class="emr-icon" />
          <span class="emr-num">1800</span>
          <span class="emr-name">Cứu hộ GT</span>
        </a>
      </div>
    </div>

    <!-- Gợi ý -->
    <div class="ofc-section">
      <div class="ofc-label">Hướng dẫn khi chờ</div>
      <div class="tips-card">
        <div class="tip-item" v-for="(tip, index) in tips" :key="index">
          <component :is="tip.icon" :size="18" class="tip-icon" :style="{ color: tip.color }" />
          <span class="tip-text">{{ tip.text }}</span>
        </div>
      </div>
    </div>

    <!-- Nút thử lại -->
    <div class="ofc-section">
      <button class="retry-btn" @click="retryConnection">
        <RefreshCw :size="16" style="margin-right:6px;" />
        Thử kết nối lại
      </button>
      <p class="retry-hint">App sẽ tự khôi phục khi có mạng</p>
    </div>

    <!-- Thông báo sao chép -->
    <transition name="toast-fade">
      <div v-if="showCopied" class="copy-toast">✅ Đã sao chép tọa độ!</div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import {
  WifiOff, MapPin, Phone, ShieldAlert, Flame,
  AlertTriangle, Copy, RefreshCw, Truck, Cross,
  Battery, Thermometer, Flashlight
} from 'lucide-vue-next';

// ── GPS ─────────────────────────────────────────────────────────
const gpsLoading = ref(true);
const gpsError = ref('');
const lat = ref(0);
const lon = ref(0);

onMounted(() => {
  // Tải GPS
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        lat.value = pos.coords.latitude;
        lon.value = pos.coords.longitude;
        gpsLoading.value = false;
      },
      () => {
        gpsLoading.value = false;
        gpsError.value = 'Không lấy được vị trí. Hãy bật GPS và cho phép truy cập.';
      },
      { timeout: 8000, enableHighAccuracy: true }
    );
  } else {
    gpsLoading.value = false;
    gpsError.value = 'Thiết bị không hỗ trợ GPS.';
  }
});

// ── Last mechanic (cached) ───────────────────────────────────────
const lastMechanic = ref(null);
onMounted(() => {
  try {
    const cached = localStorage.getItem('last_mechanic');
    if (cached) lastMechanic.value = JSON.parse(cached);
  } catch (e) {}
});

// ── Copy coords ──────────────────────────────────────────────────
const showCopied = ref(false);
const copyCoords = async () => {
  const text = `${lat.value.toFixed(6)}, ${lon.value.toFixed(6)}`;
  try {
    await navigator.clipboard.writeText(text);
  } catch (e) {
    // Trạng thái dự phòng
    const el = document.createElement('textarea');
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
  }
  showCopied.value = true;
  setTimeout(() => (showCopied.value = false), 2000);
};

// ── Retry ────────────────────────────────────────────────────────
const retryConnection = () => {
  if (navigator.onLine) {
    window.location.reload();
  } else {
    const btn = document.querySelector('.retry-btn');
    btn?.classList.add('shake');
    setTimeout(() => btn?.classList.remove('shake'), 600);
  }
};

// ── Tips ─────────────────────────────────────────────────────────
const tips = [
  { icon: Battery, color: '#10b981', text: 'Tắt màn hình để tiết kiệm pin khi chờ thợ' },
  { icon: MapPin, color: '#ef4444', text: 'Đứng ở nơi dễ nhìn thấy (lề đường, điểm mốc rõ ràng)' },
  { icon: AlertTriangle, color: '#f59e0b', text: 'Bật đèn cảnh báo khẩn cấp (hazard light) nếu đang trên đường' },
  { icon: Thermometer, color: '#f97316', text: 'Không mở nắp capo nếu động cơ đang nóng — đợi 10 phút' },
  { icon: Flashlight, color: '#3b82f6', text: 'Dùng đèn pin điện thoại báo hiệu SOS (3 ngắn - 3 dài - 3 ngắn)' },
];
</script>

<style scoped>
/* ─────── Base Layout ─────── */
.offline-page {
  min-height: 100vh;
  background: linear-gradient(160deg, #0f0c29, #1a1a2e 40%, #16213e);
  color: #e8e8f0;
  padding: 0 0 80px;
  position: relative;
  overflow: hidden;
}

/* ─────── Animated Pulse BG ─────── */
.offline-bg { position: absolute; inset: 0; pointer-events: none; }
.pulse-ring {
  position: absolute; border-radius: 50%;
  border: 1px solid rgba(239, 68, 68, 0.15);
  animation: pulseOut 4s ease-out infinite;
  top: 50px; left: 50%; transform: translateX(-50%);
}
.pulse-1 { width: 120px; height: 120px; animation-delay: 0s; }
.pulse-2 { width: 200px; height: 200px; animation-delay: 0.8s; }
.pulse-3 { width: 290px; height: 290px; animation-delay: 1.6s; }
@keyframes pulseOut {
  0%   { opacity: 0.7; transform: translateX(-50%) scale(0.8); }
  100% { opacity: 0;   transform: translateX(-50%) scale(1.4); }
}

/* ─────── Header ─────── */
.offline-header {
  display: flex; flex-direction: column; align-items: center;
  padding: 56px 20px 28px;
  position: relative; z-index: 1;
}
.offline-icon-wrap {
  width: 72px; height: 72px; border-radius: 50%;
  background: rgba(239, 68, 68, 0.15);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 16px;
  border: 1.5px solid rgba(239, 68, 68, 0.3);
  box-shadow: 0 0 30px rgba(239, 68, 68, 0.2);
}
.offline-wifi-icon { color: #ef4444; }
.offline-title {
  font-size: 26px; font-weight: 800; margin: 0 0 6px;
  letter-spacing: -0.5px;
}
.offline-sub {
  font-size: 13px; color: #9ca3af; margin: 0 0 14px; text-align: center;
  max-width: 260px; line-height: 1.6;
}
.offline-badge {
  display: flex; align-items: center; gap: 6px;
  background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 4px 12px; border-radius: 20px; font-size: 12px; color: #f87171;
}
.badge-dot {
  width: 6px; height: 6px; border-radius: 50%; background: #ef4444;
  animation: blink 1.2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

/* ─────── Sections ─────── */
.ofc-section { padding: 0 16px; margin-bottom: 14px; position: relative; z-index: 1; }
.ofc-label {
  font-size: 11px; font-weight: 700; color: #6b7280;
  text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px;
}
.ofc-card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px; padding: 14px 16px;
  backdrop-filter: blur(8px);
}
.ofc-card-header {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 600; color: #9ca3af; margin-bottom: 12px;
}

/* ─────── GPS Card ─────── */
.gps-loading {
  display: flex; align-items: center; gap: 10px;
  color: #9ca3af; font-size: 13px;
}
.gps-spinner {
  width: 18px; height: 18px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.15);
  border-top-color: #2563eb;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.gps-error { font-size: 13px; color: #f59e0b; display: flex; align-items: center; }
.coord-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.06);
}
.coord-label { font-size: 12px; color: #6b7280; }
.coord-value { font-size: 14px; font-weight: 700; color: #e2e8f0; font-family: monospace; }
.copy-btn {
  margin-top: 12px; width: 100%; padding: 8px;
  background: rgba(37, 99, 235, 0.15); border: 1px solid rgba(37, 99, 235, 0.3);
  color: #60a5fa; border-radius: 10px; font-size: 12px; font-weight: 600;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;
  transition: background 0.2s;
}
.copy-btn:active { background: rgba(37, 99, 235, 0.3); }
.gps-hint { font-size: 11px; color: #6b7280; text-align: center; margin: 6px 0 0; }

/* ─────── Last Mechanic Card ─────── */
.mechanic-card {
  display: flex; align-items: center; gap: 12px;
}
.mech-avatar {
  width: 44px; height: 44px; border-radius: 50%;
  background: linear-gradient(135deg,#2563eb,#7c3aed);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 800; color: #fff; flex-shrink: 0;
}
.mech-info { flex: 1; min-width: 0; }
.mech-name { font-size: 14px; font-weight: 700; color: #f1f5f9; }
.mech-spec { font-size: 12px; color: #9ca3af; margin-top: 2px; }
.mech-rating { font-size: 11px; color: #fbbf24; margin-top: 2px; }
.call-btn {
  display: flex; align-items: center; gap: 6px;
  background: linear-gradient(135deg, #16a34a, #15803d);
  color: #fff; border-radius: 12px; padding: 8px 14px;
  font-size: 13px; font-weight: 700; text-decoration: none;
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.35);
  flex-shrink: 0;
}

/* ─────── Emergency Contacts ─────── */
.emergency-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
}
.emr-card {
  display: flex; flex-direction: column; align-items: center;
  padding: 14px 10px; border-radius: 16px; text-decoration: none;
  transition: transform 0.15s, box-shadow 0.15s;
  border: 1px solid;
}
.emr-card:active { transform: scale(0.95); }
.emr-card.police { background: rgba(37,99,235,0.12); border-color: rgba(37,99,235,0.3); }
.emr-card.fire    { background: rgba(239,68,68,0.12);  border-color: rgba(239,68,68,0.3); }
.emr-card.medical { background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.3);}
.emr-card.towing  { background: rgba(245,158,11,0.12); border-color: rgba(245,158,11,0.3);}
.emr-icon { margin-bottom: 6px; }
.emr-card.police .emr-icon { color: #60a5fa; }
.emr-card.fire    .emr-icon { color: #f87171; }
.emr-card.medical .emr-icon { color: #34d399; }
.emr-card.towing  .emr-icon { color: #fbbf24; }
.emr-num { font-size: 20px; font-weight: 900; color: #f1f5f9; line-height: 1.1; }
.emr-name { font-size: 11px; color: #9ca3af; margin-top: 2px; }

/* ─────── Tips ─────── */
.tips-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px; overflow: hidden;
}
.tip-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.tip-item:last-child { border-bottom: none; }
.tip-icon { flex-shrink: 0; margin-top: 2px; }
.tip-text { font-size: 12.5px; color: #d1d5db; line-height: 1.5; }

/* ─────── Retry ─────── */
.retry-btn {
  width: 100%; padding: 14px;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.14);
  color: #e2e8f0; border-radius: 14px;
  font-size: 14px; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
}
.retry-btn:active { background: rgba(255,255,255,0.14); }
.retry-btn.shake { animation: shake 0.5s; }
@keyframes shake {
  0%,100%{transform:translateX(0)}
  20%,60%{transform:translateX(-6px)}
  40%,80%{transform:translateX(6px)}
}
.retry-hint { text-align: center; font-size: 11px; color: #6b7280; margin: 6px 0 0; }

/* ─────── Copy Toast ─────── */
.copy-toast {
  position: fixed; bottom: 90px; left: 50%; transform: translateX(-50%);
  background: rgba(30,30,46,0.95); color: #e2e8f0;
  padding: 10px 20px; border-radius: 20px; font-size: 13px; font-weight: 600;
  border: 1px solid rgba(255,255,255,0.15); z-index: 9999;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.toast-fade-enter-active, .toast-fade-leave-active { transition: opacity 0.3s, transform 0.3s; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateX(-50%) translateY(8px); }
</style>
