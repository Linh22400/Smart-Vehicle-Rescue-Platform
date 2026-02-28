<template>
  <div class="garage-list-container">
    <van-nav-bar title="Đặt Lịch Bảo Dưỡng" left-text="Trở lại" left-arrow @click-left="$router.go(-1)" />
    
    <van-search v-model="search" placeholder="Tìm dịch vụ, tên Gara..." />

    <div v-if="loading" class="text-center p-4">Đang tải danh sách...</div>
    <van-empty v-else-if="filteredMechanics.length === 0" description="Chưa có Gara nào. Hãy thử tìm kiếm khác." />

    <div class="p-2" v-else>
      <van-card
        v-for="mech in filteredMechanics"
        :key="mech.id"
        :title="mech.user.first_name || mech.user.username"
        :desc="mech.specialty"
        :thumb="'https://img.freepik.com/free-vector/car-repair-concept_23-2148613482.jpg'"
      >
        <template #tags>
          <van-tag type="warning">{{ mech.rating }} ★</van-tag>
          <van-tag type="primary" style="margin-left:5px">{{ mech.services.length }} dịch vụ</van-tag>
          <van-collapse v-if="mech.services.length > 0" v-model="activeNames" accordion style="margin-top:8px">
            <van-collapse-item :title="`Xem ${mech.services.length} Dịch vụ`" :name="mech.id">
                 <van-cell 
                    v-for="svc in mech.services" 
                    :key="svc.id" 
                    :title="svc.name" 
                    :label="formatPrice(svc.price)" 
                    is-link 
                    @click="bookService(mech, svc)"
                />
            </van-collapse-item>
          </van-collapse>
          <div v-else style="margin-top:8px; font-size:12px; color:#999">Chưa có dịch vụ đăng ký</div>
        </template>
      </van-card>
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
const activeNames = ref('0');

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

const formatPrice = (p) => {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(p);
}

const bookService = (mech, svc) => {
    // Navigate to Appointment Booking passing data
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
}
</script>

<style scoped>
.garage-list-container {
    background: #f7f8fa;
    min-height: 100vh;
    padding-bottom: 60px;
}
.p-2 { padding: 10px; }
</style>
