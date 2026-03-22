import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Vant from 'vant'
import 'vant/lib/index.css'
import axios from 'axios'

// --- Sửa lỗi dialog Vant hiển thị tiếng Trung: chuyển sang locale tiếng Việt ---
import { Locale } from 'vant'

const viVN = {
    name: 'vi-VN',
    // Nút dùng chung trong Dialog
    confirm: 'Xác nhận',
    cancel: 'Hủy bỏ',
    // Picker
    done: 'Xong',
    // ImagePreview
    close: 'Đóng',
    // DatePicker
    year: 'Năm', month: 'Tháng', day: 'Ngày',
    hour: 'Giờ', minute: 'Phút', second: 'Giây',
    // Uploader
    maxSize: 'Ảnh quá lớn',
    // Empty
    emptyDesc: 'Không có dữ liệu',
    // Search
    search: 'Tìm kiếm',
    // Dropdown
    select: 'Chọn',
}
Locale.use('vi-VN', viVN)

// Cấu hình Axios toàn cục — baseURL dùng Vite proxy (URL tương đối /api/...)
// Không đặt baseURL ở đây; để Vite proxy chuyển tiếp /api/* đến http://127.0.0.1:8000
axios.defaults.withCredentials = true;

const app = createApp(App)
app.use(router)
app.use(Vant)
app.mount('#app')
