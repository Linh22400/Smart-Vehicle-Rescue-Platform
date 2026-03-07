<template>
  <div class="mechanic-services-screen">
    <!-- Header -->
    <van-nav-bar
      title="Quản Lý Dịch Vụ"
      left-arrow
      @click-left="$router.back()"
      class="custom-nav-bar"
    />

    <div class="ms-content">
      <div v-if="loading" class="text-center p-4" style="color:#888;">Đang tải...</div>
      
      <van-empty v-if="!loading && services.length === 0" description="Bạn chưa có dịch vụ nào." />

      <!-- Danh sách Dịch vụ -->
      <div v-if="!loading && services.length > 0" class="ms-list">
        <div v-for="svc in services" :key="svc.id" class="ms-card">
          <div class="ms-card-body">
            <h3 class="ms-title">{{ svc.name }}</h3>
            <p v-if="svc.description" class="ms-desc">{{ svc.description }}</p>
            <div class="ms-price-line">
              <span class="ms-price-val">{{ formatPrice(svc.price) }}</span>
              <span v-if="svc.duration_minutes" class="ms-duration"><van-icon name="clock-o" /> {{ svc.duration_minutes }} phút</span>
            </div>
          </div>
          <div class="ms-card-footer">
            <van-button size="small" type="primary" plain round class="action-btn" @click="openEditDialog(svc)">
              <van-icon name="edit" /> Sửa
            </van-button>
            <van-button size="small" type="danger" plain round class="action-btn" @click="confirmDelete(svc.id)">
              <van-icon name="delete-o" /> Xóa
            </van-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Nút Thêm Mới Dịch Vụ -->
    <div class="fab-container">
      <van-button icon="plus" type="primary" round class="fab-btn" @click="openAddDialog">
        Thêm Dịch Vụ
      </van-button>
    </div>

    <!-- Dialog Thêm/Sửa Dịch vụ -->
    <van-dialog v-model:show="showDialog" :title="isEdit ? 'Sửa Dịch Vụ' : 'Thêm Dịch Vụ Mới'" show-cancel-button @confirm="saveService">
      <div class="dialog-form">
        <van-field
          v-model="form.name"
          label="Tên Dịch Vụ"
          placeholder="VD: Thay vỏ xe, Kích bình..."
          required
        />
        <van-field
          v-model="form.price"
          label="Giá Tiền"
          type="digit"
          placeholder="Số tiền VNĐ"
          required
        />
        <van-field
          v-model="form.duration_minutes"
          label="T/gian (phút)"
          type="digit"
          placeholder="Tùy chọn"
        />
        <van-field
          v-model="form.description"
          label="Mô tả"
          type="textarea"
          rows="2"
          autosize
          placeholder="Mô tả ngắn..."
        />
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { showSuccessToast, showFailToast, showConfirmDialog, showToast } from 'vant';

const services = ref([]);
const loading = ref(false);

const showDialog = ref(false);
const isEdit = ref(false);
const currentId = ref(null);

const form = ref({
  name: '',
  price: '',
  duration_minutes: '',
  description: ''
});

const formatPrice = (p) => {
  return Number(p || 0).toLocaleString('vi-VN') + ' VNĐ';
};

const fetchServices = async () => {
    loading.value = true;
    try {
        const res = await axios.get('/api/services/mechanic/services/');
        services.value = res.data;
    } catch(e) {
        console.error(e);
        showFailToast('Không thể tải dịch vụ');
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchServices();
});

const resetForm = () => {
    form.value = { name: '', price: '', duration_minutes: '', description: '' };
    currentId.value = null;
    isEdit.value = false;
};

const openAddDialog = () => {
    resetForm();
    showDialog.value = true;
};

const openEditDialog = (svc) => {
    isEdit.value = true;
    currentId.value = svc.id;
    form.value = {
        name: svc.name,
        price: svc.price,
        duration_minutes: svc.duration_minutes || '',
        description: svc.description || ''
    };
    showDialog.value = true;
};

const saveService = async () => {
    if(!form.value.name || !form.value.price) {
        showToast('Vui lòng nhập Tên và Giá dịch vụ');
        return;
    }
    
    // transform data
    const payload = {
        name: form.value.name,
        price: parseInt(form.value.price),
        description: form.value.description
    };
    if (form.value.duration_minutes) {
        payload.duration_minutes = parseInt(form.value.duration_minutes);
    }
    
    try {
        if (isEdit.value) {
            await axios.put(`/api/services/mechanic/services/${currentId.value}/`, payload);
            showSuccessToast('Đã cập nhật dịch vụ');
        } else {
            await axios.post('/api/services/mechanic/services/', payload);
            showSuccessToast('Đã thêm dịch vụ');
        }
        showDialog.value = false;
        fetchServices();
    } catch(e) {
        showFailToast('Lưu dịch vụ thất bại');
        console.error(e);
    }
};

const confirmDelete = (id) => {
    showConfirmDialog({
        title: 'Xóa dịch vụ',
        message: 'Bạn có chắc chắn muốn xóa dịch vụ này không?',
    }).then(async () => {
        try {
            await axios.delete(`/api/services/mechanic/services/${id}/`);
            showSuccessToast('Đã xóa dịch vụ');
            fetchServices();
        } catch(e) {
            showFailToast('Xóa thất bại');
        }
    }).catch(() => {});
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.mechanic-services-screen {
  background: #f4f6f9;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  padding-bottom: 80px;
}

/* Header Gradient */
:deep(.custom-nav-bar) {
  background: linear-gradient(135deg, #1a6fdf, #4f46e5) !important;
}
:deep(.custom-nav-bar .van-nav-bar__title) { color: #fff !important; font-weight: 700; }
:deep(.custom-nav-bar .van-icon) { color: #fff !important; }

.ms-content {
  padding: 16px;
}

/* Cards */
.ms-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.ms-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
  border: 1px solid #f0f2f5;
  overflow: hidden;
  transition: box-shadow 0.2s;
}
.ms-card:hover {
  box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}
.ms-card-body {
  padding: 16px;
}
.ms-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 6px 0;
}
.ms-desc {
  font-size: 13px;
  color: #666;
  margin: 0 0 10px 0;
  line-height: 1.4;
}
.ms-price-line {
  display: flex;
  align-items: center;
  gap: 12px;
}
.ms-price-val {
  font-size: 15px;
  font-weight: 800;
  color: #2563eb;
  background: #eff6ff;
  padding: 4px 10px;
  border-radius: 8px;
}
.ms-duration {
  font-size: 12px;
  color: #888;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Footer Actions */
.ms-card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 10px 16px;
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
}
.action-btn {
  height: 30px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
}

/* FAB */
.fab-container {
  position: fixed;
  bottom: 20px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  pointer-events: none;
  z-index: 100;
}
.fab-btn {
  pointer-events: auto;
  box-shadow: 0 6px 20px rgba(37,99,235,0.4);
  font-size: 15px;
  padding: 0 30px;
  height: 44px;
  background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
  border: none !important;
}

/* Dialog Form Setup */
.dialog-form {
  padding: 20px 0;
}
:deep(.dialog-form .van-field__label) {
  font-weight: 600;
  color: #555;
}
</style>
