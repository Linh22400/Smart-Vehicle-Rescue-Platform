<template>
  <div class="mechanic-container">
    <van-nav-bar title="Dashboard Thợ" />
    
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
            :tag="item.status"
            :price="item.problem_description"
            desc="Mô tả sự cố:"
            :title="`Khách hàng #${item.customer}`"
            :thumb="'https://img.freepik.com/free-icon/user_318-159711.jpg'"
        >
            <template #footer>
                <van-button v-if="item.status === 'PENDING'" size="small" type="primary" @click="updateSOSStatus(item.id, 'ACCEPTED')">Nhận Đơn</van-button>
                <van-button v-if="item.status === 'ACCEPTED'" size="small" type="success" @click="updateSOSStatus(item.id, 'COMPLETED')">Hoàn Thành</van-button>
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
            :tag="item.status"
            :price="item.service_details.name"
            :desc="`Thời gian: ${formatDate(item.appointment_time)}`"
            :title="`Khách: ${item.customer}`" 
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

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import axios from 'axios';
import { showToast } from 'vant';

const activeTab = ref('SOS');
const sosSubTab = ref('PENDING');

const sosBookings = ref([]);
const appointments = ref([]);
const stats = ref({});
const loadingSOS = ref(false);
const loadingAppt = ref(false);
const loadingStats = ref(false);

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

const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString('vi-VN');
}

const formatPrice = (p) => {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(p || 0);
}
</script>

<style scoped>
.revenue-card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.revenue-card h3 { margin: 0 0 10px 0; color: #666; font-size: 14px; }
.revenue-card .price { font-size: 28px; font-weight: bold; color: #1989fa; }
.stat-text { text-align: center; font-size: 12px; margin-top: 5px; }
.mini-price { font-weight: bold; color: #333; }
.mt-4 { margin-top: 20px; }

.chart-mock {
    background: white; padding: 15px; border-radius: 8px; text-align: center;
}
.bars { display: flex; align-items: flex-end; justify-content: space-around; height: 100px; padding-top: 10px;}
.bar { width: 10%; background: #ebedf0; border-radius: 4px; font-size: 10px; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 2px; color: #666; }

.mechanic-container {
    background: #f7f8fa;
    min-height: 100vh;
    padding-bottom: 60px;
}
.p-2 { padding: 10px; }
.mt-1 { margin-top: 5px; color: #666; font-size: 12px; }
</style>
