<template>
<van-config-provider :theme="themeClass">
<div class="app-layout" :class="themeClass">
    <router-view />

    <!-- Offline reconnected toast modern glass UI -->
    <transition name="slide-toast">
      <div v-if="showOnlineToast" class="online-toast">
        <div class="ot-icon-wrap">
          <Wifi :size="16" stroke-width="2.5" />
        </div>
        <div class="ot-text">
          <span class="ot-title">Đã kết nối trực tuyến</span>
          <span class="ot-desc">Ứng dụng hoạt động bình thường</span>
        </div>
      </div>
    </transition>

    <van-tabbar v-if="showTabbar" route>
      <van-tabbar-item replace to="/booking" icon="location-o">Cứu Hộ</van-tabbar-item>
      <van-tabbar-item replace to="/garages" icon="shop-o">Dịch Vụ</van-tabbar-item>
      <van-tabbar-item replace to="/history" icon="orders-o">Lịch Sử</van-tabbar-item>
      <van-tabbar-item replace to="/mechanic" icon="manager-o" v-if="isMechanicUser()">Thợ</van-tabbar-item>
      <van-tabbar-item replace to="/profile" icon="user-o">Tài Khoản</van-tabbar-item>
    </van-tabbar>
  </div>
</van-config-provider>
</template>

<script>
import { onMounted, onUnmounted, computed, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { globalThemeState, applyThemeToDOM } from './themeStore.js';
import { Wifi } from 'lucide-vue-next';

export default {
  components: {
    Wifi
  },
  setup() {
    const router = useRouter();
    const route = useRoute();
    const showOnlineToast = ref(false);
    let prevPath = '/booking';
    let toastTimer = null;

    const handleOffline = () => {
      console.log('App detected offline event!');
      // Lưu lại URL người dùng đang mở trước khi mất mạng
      const current = router.currentRoute.value.path;
      if (current !== '/offline') prevPath = current;
      router.push('/offline').catch(err => console.error('Router push to offline failed', err));
    };

    const handleOnline = () => {
      // Điều hướng người dùng quay lại trang trước đó
      router.push(prevPath || '/booking');
      // Hiển thị thông báo đã kết nối lại mạng
      showOnlineToast.value = true;
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => { showOnlineToast.value = false; }, 3500);
    };

    onMounted(() => {
      applyThemeToDOM(globalThemeState.value);
      window.addEventListener('offline', handleOffline);
      window.addEventListener('online', handleOnline);
      // Nếu đang mất mạng từ ngay lúc mới mở app, chuyển hướng ngay lập tức
      if (!navigator.onLine) {
        prevPath = route.path;
        router.push('/offline');
      }
    });

    onUnmounted(() => {
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('online', handleOnline);
      clearTimeout(toastTimer);
    });

    const showTabbar = computed(() => {
      const hidden = ['/login', '/register', '/offline'];
      return !hidden.includes(route.path);
    });

    return {
      themeClass: globalThemeState,
      showOnlineToast,
      showTabbar,
    };
  },
  methods: {
    isMechanicUser() {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          return user.is_mechanic;
        } catch(e) {}
      }
      return false;
    }
  }
}
</script>

<style>
body { margin: 0; padding: 0; font-family: sans-serif; transition: background 0.3s, color 0.3s; }
.app-layout { padding-bottom: 50px; min-height: 100vh; }

/* Giao diện Thông báo hiện đại khi kết nối lại mạng - Glassmorphism UI */
.online-toast {
  position: fixed; top: 16px; left: 50%; transform: translateX(-50%);
  background: rgba(22, 163, 74, 0.9);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex; align-items: center; gap: 10px;
  padding: 8px 18px 8px 10px; border-radius: 50px;
  z-index: 99999; box-shadow: 0 10px 30px rgba(22, 163, 74, 0.35);
  pointer-events: none;
}
.ot-icon-wrap {
  display: flex; align-items: center; justify-content: center;
  background: #fff; color: #16a34a;
  width: 26px; height: 26px; border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.ot-text {
  display: flex; flex-direction: column; white-space: nowrap;
}
.ot-title {
  color: #fff; font-size: 13px; font-weight: 700; line-height: 1.2; letter-spacing: -0.2px;
}
.ot-desc {
  color: rgba(255, 255, 255, 0.85); font-size: 11px; font-weight: 500; margin-top: 1px;
}
.slide-toast-enter-active, .slide-toast-leave-active {
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.slide-toast-enter-from, .slide-toast-leave-to {
  opacity: 0; transform: translateX(-50%) translateY(-24px) scale(0.9);
}

/* ============================================================
   GHI ĐÈ CSS TOÀN DIỆN CHO CHẾ ĐỘ TỐI (DARK MODE)
   Bao phủ TẤT CẢ 14 màn hình trong ứng dụng
   ============================================================ */

/* ── 1. Giao diện chung Body & Layout ── */
body.dark-theme, .app-layout.dark {
    background: #121212 !important;
    color: #e0e0e0;
}

/* ── 2. Ghi đè màu nền (Background) cho từng Màn hình ── */
.dark-theme .history-container,
.dark-theme .history-page,
.dark-theme .profile-page,
.dark-theme .mechanic-profile-screen,
.dark-theme .mechanic-container,
.dark-theme .gl-container,
.dark-theme .garage-page,
.dark-theme .mechanic-services-screen,
.dark-theme .appointment-container,
.dark-theme .personal-info-screen,
.dark-theme .settings-screen,
.dark-theme .booking-page,
.dark-theme .profile-content {
    background-color: #121212 !important;
}

/* ── 3. Ghi đè Components của thư viện Vant ── */
.dark-theme .van-nav-bar { background-color: #1a1a1c !important; }
.dark-theme .van-cell,
.dark-theme .van-cell-group,
.dark-theme .van-cell-group--inset { background-color: #1e1e1e !important; }
.dark-theme .van-cell__title, .dark-theme .van-cell__value { color: #e0e0e0 !important; }
.dark-theme .van-cell-group__title { color: #999 !important; }
.dark-theme .van-field__label { color: #aaa !important; }
.dark-theme .van-field__control { color: #e0e0e0 !important; }
.dark-theme .van-field__control::placeholder { color: #666 !important; }
.dark-theme .van-popup { background: #1e1e1e !important; }
.dark-theme .van-empty__description { color: #a0a0a0 !important; }
.dark-theme .van-notice-bar { background: #2c2c2e !important; border: 1px solid #444 !important; }
.dark-theme .van-tabs__wrap, .dark-theme .van-tabs__nav { background-color: #121212 !important; border-color: #333 !important; }
.dark-theme .van-tab { color: #999 !important; }
.dark-theme .van-tab--active { color: #fff !important; font-weight: bold; }
.dark-theme .van-tabbar { background-color: #1a1a1c !important; border-top: 1px solid #333 !important; }
.dark-theme .van-tabbar-item { background-color: transparent !important; color: #aaa !important; }
.dark-theme .van-tabbar-item--active { background-color: transparent !important; color: #64b5f6 !important; font-weight: bold; }
.dark-theme .van-action-sheet { background: #1e1e1e !important; }
.dark-theme .van-action-sheet__header { color: #e0e0e0 !important; }
.dark-theme .van-action-sheet__item { color: #e0e0e0 !important; background: #1e1e1e !important; }
.dark-theme .van-action-sheet__cancel { color: #e0e0e0 !important; background: #1a1a1c !important; }
.dark-theme .van-action-sheet__gap { background: #121212 !important; }
.dark-theme .van-loading__text { color: #aaa !important; }
.dark-theme .van-toast { background: #2c2c2e !important; }

/* ── 4. Ghi đè Vant Dialog ── */
.dark-theme .van-dialog { background-color: #2c2c2e !important; }
.dark-theme .van-dialog__header { color: #f5f5f5 !important; }
.dark-theme .van-dialog__message,
.dark-theme .van-dialog__content p,
.dark-theme .rating-content p { color: #e0e0e0 !important; }
.dark-theme .van-dialog__footer { background-color: #1e1e1e !important; }
.dark-theme .van-dialog .van-button { background-color: transparent !important; border-top: 1px solid #444 !important; }
.dark-theme .van-dialog .van-dialog__cancel,
.dark-theme .van-dialog .van-button--default { color: #e0e0e0 !important; border-right: 1px solid #444 !important; }
.dark-theme .van-dialog .van-dialog__confirm { color: #64b5f6 !important; }
.dark-theme .van-dialog .van-field { background-color: #1e1e1e !important; border-color: #444 !important; }
.dark-theme .van-dialog .van-field__control,
.dark-theme .van-dialog .van-field__label { color: #e0e0e0 !important; }

/* ── 5. Các thẻ thông tin & Containers (Tất cả Màn hình) ── */
.dark-theme .hst-card,
.dark-theme .ai-history-card,
.dark-theme .info-card,
.dark-theme .menu-card,
.dark-theme .edit-popup,
.dark-theme .tracking-info,
.dark-theme .payment-container,
.dark-theme .detail-container,
.dark-theme .order-card,
.dark-theme .gl-card,
.dark-theme .ms-card,
.dark-theme .revenue-card,
.dark-theme .chart-mock,
.dark-theme .map-header,
.dark-theme .user-info,
.dark-theme .login-container,
.dark-theme .garage-card,
.dark-theme .mech-grid-card,
.dark-theme .mfp-card,
.dark-theme .waiting-card,
.dark-theme .ai-card,
.dark-theme .ai-stat-box,
.dark-theme .ai-recommendation,
.dark-theme .ai-parts-wrap,
.dark-theme .ai-diagnosis-card,
.dark-theme .ai-price-card,
.dark-theme .search-wrap,
.dark-theme .stats-mini {
    background-color: #1e1e1e !important;
    color: #e0e0e0 !important;
    border-color: #333 !important;
}

/* ── 6. Header & Footer của Thẻ (Cards) ── */
.dark-theme .chat-header,
.dark-theme .chat-footer,
.dark-theme .order-footer,
.dark-theme .order-header,
.dark-theme .gl-card-footer,
.dark-theme .gl-card-header,
.dark-theme .ms-card-footer,
.dark-theme .hst-footer,
.dark-theme .hst-card-header,
.dark-theme .aih-footer,
.dark-theme .cleanup-bar,
.dark-theme .tracking-header,
.dark-theme .detail-header,
.dark-theme .ai-header,
.dark-theme .ai-price-header,
.dark-theme .ai-total-box {
    background: #1e1e1e !important;
    border-color: #333 !important;
}

/* ── 7. Bảng trượt nổi (Floating Panels - BookingScreen Mechanic Picker) ── */
.dark-theme .mfp-header,
.dark-theme .mfp-scroll {
    background: rgba(30,30,30,0.96) !important;
    backdrop-filter: blur(10px);
    border-color: #333 !important;
}
.dark-theme .mfp-title { color: #e0e0e0 !important; }
.dark-theme .mfp-close { background: #333 !important; color: #e0e0e0 !important; }
.dark-theme .mfp-name, .dark-theme .mgc-name { color: #e0e0e0 !important; }
.dark-theme .mfp-spec, .dark-theme .mgc-spec, .dark-theme .mgc-meta { color: #999 !important; }
.dark-theme .mfp-stat { background: #333 !important; color: #ccc !important; }
.dark-theme .mfp-stat.star { background: #3a3000 !important; color: #ffd21e !important; }

/* ── 8. Dialog Trí tuệ AI (BookingScreen) ── */
.dark-theme .ai-wrap,
.dark-theme .ai-upload-state,
.dark-theme .ai-tab-content {
    background: #121212 !important;
}
.dark-theme .ai-header-title,
.dark-theme .ai-upload-title,
.dark-theme .ai-analyzing-text,
.dark-theme .ai-card-value,
.dark-theme .ai-status-label,
.dark-theme .ai-modal-header { color: #e0e0e0 !important; }
.dark-theme .ai-header-sub,
.dark-theme .ai-upload-desc,
.dark-theme .ai-analyzing-sub,
.dark-theme .ai-card-label,
.dark-theme .ai-stat-label,
.dark-theme .ai-hint,
.dark-theme .ai-card-detail,
.dark-theme .ai-rec-text,
.dark-theme .ai-section-head,
.dark-theme .apr-label,
.dark-theme .apr-range { color: #999 !important; }
.dark-theme .ai-divider { background: #333 !important; }
.dark-theme .ai-powered-badge { background: #2c2c2e !important; color: #999 !important; }
.dark-theme .ai-btn-secondary {
    background: #2c2c2e !important;
    color: #e0e0e0 !important;
    border-color: #555 !important;
}
.dark-theme .ai-modal-header { background: #1e1e1e !important; border-color: #333 !important; }
.dark-theme .ai-price-header { background: #1a2744 !important; border-color: #333 !important; }
.dark-theme .ai-price-row { border-color: #333 !important; }
.dark-theme .ai-price-row.total { background: #1a2744 !important; }
.dark-theme .ai-total-box { background: #1a2744 !important; border-color: #333 !important; }
.dark-theme .ai-total-label, .dark-theme .ai-total-range { color: #999 !important; }
.dark-theme .ai-price-note { background: #2c2200 !important; border-color: #554400 !important; color: #e0c060 !important; }
.dark-theme .ai-warning-box { background: #2c1010 !important; border-color: #663333 !important; }
.dark-theme .ai-warn-title { color: #ff6b6b !important; }
.dark-theme .ai-warn-text { color: #e08080 !important; }
.dark-theme .btn-record-start { background: #1a2744 !important; border-color: #333 !important; }
.dark-theme .btn-upload-audio { background: #1e1e1e !important; border-color: #444 !important; color: #aaa !important; }
.dark-theme .mechanic-drawer { background: #121212 !important; }

/* ── 9. Màn hình chờ (Waiting Overlay - BookingScreen) ── */
.dark-theme .waiting-card { background: #1e1e1e !important; }
.dark-theme .waiting-title { color: #e0e0e0 !important; }
.dark-theme .waiting-desc { color: #999 !important; }
.dark-theme .waiting-id { color: #666 !important; }

/* ── 10. Components Chat ── */
.dark-theme .chat-body { background: #121212 !important; }
.dark-theme .msg-them .msg-bubble { background: #2c2c2e !important; color: #e0e0e0 !important; border-color: #444 !important; }
.dark-theme .chat-header h3 { color: #e0e0e0 !important; }

/* ── 11. Các thẻ CSS riêng của GarageListScreen ── */
.dark-theme .gl-search-bar { background-color: #121212 !important; }
.dark-theme .gl-search-bar input { background-color: #1e1e1e !important; color: #e0e0e0 !important; border: 1px solid #333; }
.dark-theme .gl-price { color: #64b5f6 !important; }
.dark-theme .gc-name { color: #e0e0e0 !important; }
.dark-theme .gc-spec { color: #999 !important; }
.dark-theme .gc-toggle { background: #2c2c2e !important; color: #64b5f6 !important; }
.dark-theme .gc-toggle:active { background: #1a2744 !important; }
.dark-theme .gc-badge.rating { background: #3a3000 !important; }
.dark-theme .gc-badge.svc { background: #1a2744 !important; }
.dark-theme .search-input { color: #e0e0e0 !important; }
.dark-theme .search-input::placeholder { color: #666 !important; }
.dark-theme .gc-svc-name { color: #e0e0e0 !important; }
.dark-theme .gc-services { border-color: #333 !important; }
.dark-theme .gc-svc-item:hover, .dark-theme .gc-svc-item:active { background: #2c2c2e !important; }

/* ── 12. Các thẻ CSS riêng của MechanicProfileScreen ── */
.dark-theme .mechanic-name { color: #e0e0e0 !important; }
.dark-theme .role-tag { background: #1a2744 !important; color: #64b5f6 !important; }

/* ── 13. Màu Sắc Văn Bản (Text Colors) ── */
.dark-theme .text-gray-700,
.dark-theme .info-label,
.dark-theme .detail-label,
.dark-theme .order-sub,
.dark-theme .gl-address,
.dark-theme .gl-distance,
.dark-theme .ms-desc,
.dark-theme .order-field,
.dark-theme .sm-label,
.dark-theme .hst-date,
.dark-theme .hst-row,
.dark-theme .aih-date,
.dark-theme .aih-detail,
.dark-theme .cleanup-info,
.dark-theme .payment-subtitle,
.dark-theme .pm-label,
.dark-theme .diagnosis-text,
.dark-theme .details-text {
    color: #a0a0a0 !important;
}
.dark-theme .detail-value,
.dark-theme .order-title,
.dark-theme .info-value,
.dark-theme .profile-name,
.dark-theme .gl-title,
.dark-theme .ms-title,
.dark-theme .menu-item-label,
.dark-theme .sm-count,
.dark-theme .aih-diagnosis,
.dark-theme .payment-title,
.dark-theme .tracking-mechanic {
    color: #e0e0e0 !important;
}
.dark-theme .tracking-title,
.dark-theme .detail-title,
.dark-theme .hst-title,
.dark-theme .order-field strong {
    color: #e0e0e0 !important;
}
.dark-theme .revenue-card h3,
.dark-theme .chart-mock p,
.dark-theme .mt-1,
.dark-theme .stat-text {
    color: #aaa !important;
}

/* ── 14. Vạch Ngăn Cách & Đường Viền (Dividers & Borders) ── */
.dark-theme .menu-divider,
.dark-theme .info-divider,
.dark-theme .hst-divider { background-color: #2a2a2a !important; }
.dark-theme .menu-item:active { background: #2a2a2a !important; }
.dark-theme .menu-item-label { color: #e0e0e0 !important; }
.dark-theme .menu-group-label { color: #777 !important; }
.dark-theme .edit-popup-header { border-color: #333 !important; }
.dark-theme .edit-popup-title { color: #e0e0e0 !important; }
.dark-theme .ep-section-label { color: #aaa !important; }
.dark-theme .detail-row.cancel { background: #2c1010 !important; }
.dark-theme .detail-row.cancel .detail-value { color: #ff6b6b !important; }
.dark-theme .detail-row.cancel .detail-label { color: #e08080 !important; }
.dark-theme .detail-row.highlight { background: #2c2200 !important; }
.dark-theme .payment-method-card { border-color: #444 !important; }

/* ── 15. Menu Chức Năng & Hồ Sơ (Menu & Profile) ── */
.dark-theme .menu-item-icon { background: #333 !important; }
.dark-theme .logout-btn { color: #ff5252 !important; background: #1e1e1e !important; border-color: #333 !important; }
.dark-theme .profile-hero { background: linear-gradient(135deg, #1a2744, #1e1e3f) !important; }
.dark-theme .edit-btn { background: #1e1e1e !important; color: #64b5f6 !important; border-color: #333 !important; }

/* ── 16. Bộ Lọc & Tìm Kiếm (Filter & Search) ── */
.dark-theme .pill { background: #2c2c2e !important; color: #aaa !important; }
.dark-theme .pill.active { background: #2563eb !important; color: #fff !important; }
.dark-theme .filter-bar .van-field,
.dark-theme .filter-bar .van-cell__value { background: #1e1e1e !important; }
.dark-theme .filter-bar input { color: #e0e0e0 !important; }

/* ── 17. Popup Chỉnh Sửa (ProfileScreen) ── */
.dark-theme .ep-title { color: #e0e0e0 !important; }
.dark-theme .ep-label { color: #aaa !important; }
.dark-theme .ep-input,
.dark-theme .ep-input-wrap { background: #2c2c2e !important; border-color: #444 !important; color: #e0e0e0 !important; }

/* ── 18. SettingsScreen / AppointmentScreen ── */
.dark-theme .settings-screen,
.dark-theme .appointment-container { background: #121212 !important; }
.dark-theme input[type="datetime-local"] { color: #e0e0e0 !important; color-scheme: dark; }

/* ── 19. Ghi Đè Thẻ Vant (SOS & Lịch Hẹn) ── */
.dark-theme .van-card { background: #1e1e1e !important; }
.dark-theme .van-card__title { color: #e0e0e0 !important; }
.dark-theme .van-card__price { color: #64b5f6 !important; }
.dark-theme .van-card__desc { color: #999 !important; }
.dark-theme .van-card__footer { background: #1a1a1c !important; border-color: #333 !important; }
.dark-theme .van-tag { border-color: #444 !important; }

/* ── Ghi Đè Nút Nhấn Cơ Bản (Button Overrides cho GPS, v.v...) ── */
.dark-theme .van-button--plain { background: #1e1e1e !important; border-color: #444 !important; }
.dark-theme .van-button--primary.van-button--plain { background: #1a2744 !important; color: #64b5f6 !important; border-color: #2563eb !important; }
.dark-theme .van-button--success.van-button--plain { background: #1a3320 !important; color: #4caf50 !important; border-color: #388e3c !important; }
.dark-theme .van-button--danger.van-button--plain { background: #2c1010 !important; color: #ff6b6b !important; border-color: #c62828 !important; }
.dark-theme .van-button--warning.van-button--plain { background: #2c1900 !important; color: #ffb74d !important; border-color: #e65100 !important; }
/* Tính chất đặc thù mạnh hơn để ghi đè các thẻ CSS đóng block (scoped) của component */
.dark-theme .mechanic-profile-screen .van-button--primary.van-button--plain,
.dark-theme .mechanic-profile-screen .van-button--primary.van-button--plain:not(.van-button--loading) { background: #1a2744 !important; color: #64b5f6 !important; border-color: #2563eb !important; }
.dark-theme .mechanic-services-screen .van-button--primary.van-button--plain { background: #1a2744 !important; color: #64b5f6 !important; border-color: #2563eb !important; }

/* ── 20. Thành Phần Khác (Misc) ── */
.dark-theme .hst-body { color: #a0a0a0 !important; }
.dark-theme .aih-price { color: #64b5f6 !important; }
.dark-theme .sm-price { color: #64b5f6 !important; }
.dark-theme .mini-price { color: #64b5f6 !important; }
.dark-theme .detail-value.cost { color: #ff6b6b !important; }
.dark-theme .payment-amount { color: #ff6b6b !important; }
.dark-theme .rated-badge { color: #4caf50 !important; }
.dark-theme .paid-badge { background: #1a3a20 !important; color: #4caf50 !important; }
.dark-theme .bar { background: linear-gradient(180deg, #64b5f6, #2563eb) !important; }

/* ── 21. Thống Kê Của Thợ (MechanicDashboard Stats) ── */
.dark-theme .stats-mini { background: #1e1e1e !important; }
.dark-theme .sm-count { color: #e0e0e0 !important; }
.dark-theme .stats-subtitle { color: #aaa !important; }
.dark-theme .cancelled-stat { background: #2c1010 !important; color: #ff6b6b !important; }
.dark-theme .van-grid-item__content { background: #1e1e1e !important; }
.dark-theme .van-grid-item__text { color: #e0e0e0 !important; }
.dark-theme .revenue-card { background: #1e1e1e !important; }
.dark-theme .revenue-card .price { color: #64b5f6 !important; }

/* ── 22. Bảng Chọn Xe SOS (BookingScreen Vehicle Selection) ── */
.dark-theme .vehicle-selection { background: #1e1e1e !important; }
.dark-theme .vehicle-selection p { color: #e0e0e0 !important; }
.dark-theme .van-radio__label { color: #e0e0e0 !important; }
.dark-theme .van-radio-group { color: #e0e0e0 !important; }
.dark-theme .fab-panel { background: transparent !important; }
</style>
