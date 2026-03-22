<template>
  <div class="stats-wrap">
    <!-- Đang tải -->
    <div v-if="loading" class="stats-loading">
      <van-loading size="28" color="#2563eb" />
      <p>Đang tải thống kê...</p>
    </div>

    <template v-else>
      <!-- ── Summary Cards ── -->
      <div class="summary-grid">
        <div class="stat-card blue">
          <div class="stat-icon">💰</div>
          <div class="stat-body">
            <div class="stat-value">{{ formatMoney(data.total_revenue) }}</div>
            <div class="stat-label">Tổng doanh thu</div>
          </div>
        </div>
        <div class="stat-card green">
          <div class="stat-icon">✅</div>
          <div class="stat-body">
            <div class="stat-value">{{ totalCompleted }}</div>
            <div class="stat-label">Đơn hoàn thành</div>
          </div>
        </div>
        <div class="stat-card orange">
          <div class="stat-icon">🚨</div>
          <div class="stat-body">
            <div class="stat-value">{{ data.sos_stats?.count || 0 }}</div>
            <div class="stat-label">SOS đã giải quyết</div>
          </div>
        </div>
        <div class="stat-card gold">
          <div class="stat-icon">⭐</div>
          <div class="stat-body">
            <div class="stat-value">{{ data.rating?.toFixed(1) || '—' }}</div>
            <div class="stat-label">Điểm đánh giá</div>
          </div>
        </div>
      </div>

      <!-- ── Bar Chart: Doanh thu 7 ngày ── -->
      <div class="chart-card">
        <div class="chart-title">📊 Doanh Thu 7 Ngày Gần Nhất</div>
        <div class="chart-inner">
          <Bar :data="barData" :options="barOptions" />
        </div>
      </div>

      <!-- ── Line Chart: Số đơn mỗi ngày ── -->
      <div class="chart-card">
        <div class="chart-title">📈 Số Đơn Theo Ngày</div>
        <div class="chart-inner">
          <Line :data="lineData" :options="lineOptions" />
        </div>
      </div>

      <!-- ── Doughnut: Trạng thái đơn hàng ── -->
      <div class="chart-card doughnut-card">
        <div class="chart-title">🥧 Tỉ Lệ Đơn Hàng</div>
        <div class="chart-inner doughnut-inner">
          <Doughnut :data="doughnutData" :options="doughnutOptions" />
        </div>
        <!-- Chú giải màu sắc -->
        <div class="legend-list">
          <div class="legend-item" v-for="(item, i) in legendItems" :key="i">
            <span class="legend-dot" :style="{ background: item.color }"></span>
            <span>{{ item.label }}: <b>{{ item.value }}</b></span>
          </div>
        </div>
      </div>

      <!-- ── Week vs Month ── -->
      <div class="period-grid">
        <div class="period-card">
          <div class="period-head">📅 7 ngày qua</div>
          <div class="period-row"><span>SOS</span><b>{{ data.sos_stats?.week?.count || 0 }} đơn — {{ formatMoney(data.sos_stats?.week?.revenue) }}</b></div>
          <div class="period-row"><span>Dịch vụ</span><b>{{ data.service_stats?.week?.count || 0 }} đơn — {{ formatMoney(data.service_stats?.week?.revenue) }}</b></div>
        </div>
        <div class="period-card">
          <div class="period-head">🗓️ 30 ngày qua</div>
          <div class="period-row"><span>SOS</span><b>{{ data.sos_stats?.month?.count || 0 }} đơn — {{ formatMoney(data.sos_stats?.month?.revenue) }}</b></div>
          <div class="period-row"><span>Dịch vụ</span><b>{{ data.service_stats?.month?.count || 0 }} đơn — {{ formatMoney(data.service_stats?.month?.revenue) }}</b></div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale, LinearScale,
  BarElement, LineElement, PointElement, ArcElement,
  Title, Tooltip, Legend, Filler
} from 'chart.js';
import { Bar, Doughnut, Line } from 'vue-chartjs';

ChartJS.register(
  CategoryScale, LinearScale,
  BarElement, LineElement, PointElement, ArcElement,
  Title, Tooltip, Legend, Filler
);

const loading = ref(true);
const data = ref({});

onMounted(async () => {
  try {
    const res = await axios.get('/api/services/mechanic/revenue/');
    data.value = res.data;
  } catch (e) {
    console.error('Stats error:', e);
  } finally {
    loading.value = false;
  }
});

// ── Hàm tiện ích ────────────────────────────────────────────────────────────
const formatMoney = (v) => {
  if (!v) return '0 VNĐ';
  return Number(v).toLocaleString('vi-VN') + ' VNĐ';
};

const totalCompleted = computed(() =>
  (data.value.sos_stats?.count || 0) + (data.value.service_stats?.count || 0)
);

// ── Bar chart: doanh thu mỗi ngày ────────────────────────────────
const barData = computed(() => ({
  labels: data.value.chart?.labels || [],
  datasets: [
    {
      label: 'SOS',
      data: data.value.chart?.sos_revenue || [],
      backgroundColor: 'rgba(239, 68, 68, 0.75)',
      borderRadius: 6,
    },
    {
      label: 'Dịch vụ',
      data: data.value.chart?.svc_revenue || [],
      backgroundColor: 'rgba(37, 99, 235, 0.75)',
      borderRadius: 6,
    },
  ],
}));
const barOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: { legend: { position: 'top' } },
  scales: {
    y: {
      ticks: { callback: (v) => (v >= 1000 ? (v / 1000) + 'K' : v) },
    },
  },
};

// ── Line chart: số đơn mỗi ngày ────────────────────────────────
const lineData = computed(() => ({
  labels: data.value.chart?.labels || [],
  datasets: [{
    label: 'Số đơn',
    data: data.value.chart?.orders || [],
    borderColor: '#7c3aed',
    backgroundColor: 'rgba(124, 58, 237, 0.12)',
    fill: true,
    tension: 0.4,
    pointRadius: 5,
    pointBackgroundColor: '#7c3aed',
  }],
}));
const lineOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: { legend: { position: 'top' } },
  scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
};

// ── Doughnut chart: trạng thái đơn ────────────────────────────
const STATUS_COLORS = ['#07c160', '#ee0a24', '#ff9500', '#2563eb'];
const STATUS_LABELS = ['Hoàn thành', 'Hủy', 'Đang xử lý', 'Chờ nhận'];

const doughnutData = computed(() => {
  const sb = data.value.status_breakdown || {};
  return {
    labels: STATUS_LABELS,
    datasets: [{
      data: [
        sb.COMPLETED || 0,
        sb.CANCELLED || 0,
        sb.IN_PROGRESS || 0,
        sb.PENDING || 0,
      ],
      backgroundColor: STATUS_COLORS,
      borderWidth: 2,
      borderColor: '#fff',
    }],
  };
});
const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: true,
  cutout: '65%',
  plugins: { legend: { display: false } },
};

const legendItems = computed(() => {
  const sb = data.value.status_breakdown || {};
  const vals = [sb.COMPLETED || 0, sb.CANCELLED || 0, sb.IN_PROGRESS || 0, sb.PENDING || 0];
  return STATUS_LABELS.map((label, i) => ({
    label, color: STATUS_COLORS[i], value: vals[i]
  }));
});
</script>

<style scoped>
.stats-wrap { padding: 12px; }
.stats-loading { text-align: center; padding: 48px 0; color: #999; }

/* Thẻ thống kê tổng quan */
.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 16px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 12px;
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}
.stat-card.blue  { border-left: 4px solid #2563eb; }
.stat-card.green { border-left: 4px solid #07c160; }
.stat-card.orange{ border-left: 4px solid #ef4444; }
.stat-card.gold  { border-left: 4px solid #f59e0b; }
.stat-icon { font-size: 22px; }
.stat-value { font-size: 15px; font-weight: 800; color: #111; }
.stat-label { font-size: 10px; color: #888; margin-top: 1px; }

/* Biểu đồ */
.chart-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.chart-title {
  font-size: 13px;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
}
.chart-inner { width: 100%; }
.doughnut-inner { max-width: 220px; margin: 0 auto; }

/* Chú giải doughnut */
.legend-list { margin-top: 12px; display: flex; flex-direction: column; gap: 6px; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #555; }
.legend-dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }

/* Lưới thống kê theo kỳ (tuần/tháng) */
.period-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.period-card {
  background: #fff;
  border-radius: 14px;
  padding: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}
.period-head { font-size: 12px; font-weight: 700; color: #555; margin-bottom: 8px; }
.period-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #777;
  margin-bottom: 4px;
}
.period-row b { color: #111; }
</style>
