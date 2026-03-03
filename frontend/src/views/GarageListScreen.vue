<template>
  <div class="garage-page">
    <!-- Header -->
    <div class="garage-hero">
      <van-icon name="arrow-left" size="20" color="#fff" @click="$router.go(-1)" class="back-icon" />
      <div class="garage-hero-text">
        <div class="garage-hero-title">Đặt Lịch Bảo Dưỡng</div>
        <div class="garage-hero-sub">Chọn Gara & dịch vụ phù hợp</div>
      </div>
    </div>

    <!-- Search -->
    <div class="search-wrap">
      <van-icon name="search" size="16" color="#aaa" />
      <input v-model="search" class="search-input" placeholder="Tìm dịch vụ, tên Gara..." />
    </div>

    <!-- States -->
    <div v-if="loading" class="loading-state">
      <van-loading size="28" color="#2563eb" />
      <p>Đang tải danh sách Gara...</p>
    </div>
    <van-empty v-else-if="filteredMechanics.length === 0" image="search" description="Không tìm thấy Gara nào" />

    <!-- Grid -->
    <div class="garage-grid" v-else>
      <div
        v-for="mech in filteredMechanics"
        :key="mech.id"
        class="garage-card"
        :class="{ 'expanded': openGarage === mech.id }"
      >
        <!-- Card Header -->
        <div class="gc-top">
          <div class="gc-avatar">
            <van-icon name="shop-o" size="22" color="#fff" />
          </div>
          <div class="gc-info">
            <div class="gc-name">{{ mech.user.first_name || mech.user.username }}</div>
            <div class="gc-spec">{{ mech.specialty || 'Đa dịch vụ' }}</div>
          </div>
        </div>

        <!-- Badges -->
        <div class="gc-badges">
          <span class="gc-badge rating">
            <van-icon name="star" size="10" color="#e67e00" /> {{ mech.rating }}
          </span>
          <span class="gc-badge svc">{{ mech.services.length }} dịch vụ</span>
        </div>

        <!-- Expand Toggle -->
        <button
          v-if="mech.services.length > 0"
          class="gc-toggle"
          @click.stop="toggleCollapse(mech.id)"
        >
          {{ openGarage === mech.id ? 'Ẩn bớt' : 'Xem dịch vụ' }}
          <van-icon :name="openGarage === mech.id ? 'arrow-up' : 'arrow-down'" size="11" />
        </button>
        <div v-else class="gc-no-svc">Chưa có dịch vụ</div>

        <!-- Services (expanded) -->
        <transition name="expand">
          <div v-if="openGarage === mech.id" class="gc-services">
            <div
              v-for="svc in mech.services"
              :key="svc.id"
              class="gc-svc-item"
              @click="bookService(mech, svc)"
            >
              <div class="gc-svc-info">
                <div class="gc-svc-name">{{ svc.name }}</div>
                <div class="gc-svc-price">{{ formatPrice(svc.price) }}</div>
              </div>
              <van-icon name="arrow" size="13" color="#2563eb" />
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const mechanics = ref([]);
const loading = ref(true);
const search = ref('');
const openGarage = ref(null);

onMounted(async () => {
  try {
    const res = await axios.get('/api/services/garages/');
    mechanics.value = res.data;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
});

const filteredMechanics = computed(() => {
  if (!search.value) return mechanics.value;
  const q = search.value.toLowerCase();
  return mechanics.value.filter(m =>
    (m.user.first_name && m.user.first_name.toLowerCase().includes(q)) ||
    m.specialty.toLowerCase().includes(q) ||
    m.services.some(s => s.name.toLowerCase().includes(q))
  );
});

const toggleCollapse = (id) => {
  openGarage.value = openGarage.value === id ? null : id;
};

const formatPrice = (p) =>
  new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(p);

const bookService = (mech, svc) => {
  router.push({
    path: '/appointment',
    query: {
      mechanicId: mech.id,
      mechanicName: mech.user.first_name || mech.user.username,
      serviceId: svc.id,
      serviceName: svc.name,
      price: svc.price
    }
  });
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

.garage-page {
  min-height: 100vh;
  background: #f3f4f8;
  font-family: 'Inter', sans-serif;
  padding-bottom: 70px;
}

/* ─── Hero ─── */
.garage-hero {
  background: linear-gradient(135deg, #1a6fdf, #4f46e5);
  padding: 18px 16px 22px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.back-icon { cursor: pointer; flex-shrink: 0; }
.garage-hero-title { color: #fff; font-size: 18px; font-weight: 700; }
.garage-hero-sub { color: rgba(255,255,255,0.75); font-size: 12px; margin-top: 2px; }

/* ─── Search ─── */
.search-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border-radius: 12px;
  padding: 10px 14px;
  margin: 12px 12px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.07);
}
.search-input {
  flex: 1; border: none; outline: none;
  font-size: 14px; color: #333; background: transparent;
}
.search-input::placeholder { color: #bbb; }

/* Loading */
.loading-state { text-align: center; padding: 40px 20px; color: #888; font-size: 14px; }
.loading-state p { margin-top: 10px; }

/* ─── 2-Column Grid ─── */
.garage-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding: 0 12px;
}

/* ─── Garage Card ─── */
.garage-card {
  background: #fff;
  border-radius: 16px;
  padding: 14px 12px 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
  border: 1.5px solid #eef0f5;
  transition: box-shadow 0.2s;
  align-self: start;
}
.garage-card.expanded {
  box-shadow: 0 4px 18px rgba(37,99,235,0.12);
  border-color: #c7d7ff;
}

/* Top row */
.gc-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.gc-avatar {
  width: 42px; height: 42px; flex-shrink: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 3px 8px rgba(37,99,235,0.3);
}
.gc-info { min-width: 0; }
.gc-name {
  font-size: 13px; font-weight: 800; color: #111;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.gc-spec {
  font-size: 11px; font-weight: 600; color: #666;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  margin-top: 1px;
}

/* Badges */
.gc-badges { display: flex; gap: 5px; margin-bottom: 9px; flex-wrap: wrap; }
.gc-badge {
  display: inline-flex; align-items: center; gap: 3px;
  font-size: 11px; font-weight: 700;
  padding: 2px 8px; border-radius: 20px;
}
.rating { background: #fff8e1; color: #b45309; }
.svc    { background: #e0eaff; color: #2563eb; }

/* Toggle button */
.gc-toggle {
  width: 100%;
  display: flex; align-items: center; justify-content: center; gap: 4px;
  padding: 7px 0;
  background: #f3f4f8;
  border: none; border-radius: 8px;
  font-size: 12px; font-weight: 700; color: #2563eb;
  cursor: pointer;
  transition: background 0.15s;
}
.gc-toggle:active { background: #e0eaff; }
.gc-no-svc { font-size: 11px; color: #bbb; text-align: center; padding: 6px 0; }

/* Services list (expanded) */
.gc-services { margin-top: 10px; border-top: 1px solid #f0f0f0; padding-top: 8px; }
.gc-svc-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 9px 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.12s;
}
.gc-svc-item:active { background: #f3f4f8; }
.gc-svc-name { font-size: 13px; font-weight: 600; color: #222; }
.gc-svc-price { font-size: 12px; font-weight: 700; color: #2563eb; margin-top: 2px; }

/* Expand animation */
.expand-enter-active { transition: all 0.25s ease; overflow: hidden; }
.expand-leave-active { transition: all 0.2s ease;  overflow: hidden; }
.expand-enter-from, .expand-leave-to { max-height: 0; opacity: 0; }
.expand-enter-to,   .expand-leave-from { max-height: 500px; opacity: 1; }
</style>
