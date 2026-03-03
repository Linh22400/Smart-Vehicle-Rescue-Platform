import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Vant from 'vant'
import 'vant/lib/index.css'
import axios from 'axios'

// --- Fix tiếng Trung trên dialog Vant: set locale sang tiếng Việt ---
import { Locale } from 'vant'

const viVN = {
    name: 'vi-VN',
    // Dialog & shared buttons
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

// Global Axios Config
axios.defaults.withCredentials = true;
axios.defaults.baseURL = 'http://localhost:8000';

const app = createApp(App)
app.use(router)
app.use(Vant)
app.mount('#app')
