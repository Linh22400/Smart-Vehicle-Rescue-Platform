<div align="center">
  <img src="https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D" alt="VueJS"/>
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green" alt="Django"/>
  <img src="https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E" alt="Vite"/>
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini_AI"/>
</div>

# 🚗 Smart Vehicle Rescue Platform (Nền tảng Cứu hộ Xe Thông minh)

## 📌 Giới thiệu dự án
Đây là Hệ thống Ứng dụng PWA kết nối Khách hàng với Thợ sửa chữa xe cơ giới theo Thời gian thực (Real-time tracking). Khác biệt lớn nhất của đồ án là việc tích hợp **Trí tuệ Nhân tạo (Gemini 2.5 Flash Native Audio/Vision)** để chẩn đoán hư hỏng tự động qua Hình ảnh và Tiếng động cơ, đồng thời đưa ra dự toán chi phí chuẩn xác dựa trên báo giá phụ tùng tại thị trường Việt Nam (Prompt Grounding).

Từ đó, Khách hàng sẽ không còn sợ cảnh "thợ vẽ bệnh, hét giá", và Thợ cũng dễ dàng tìm được nguồn khách đều đặn thông qua tính năng SOS Bán kính 5km.

---

## 🚀 Công nghệ sử dụng
### Phía Frontend (Ứng dụng Khách/Thợ)
- **Framework:** Vue.js 3 (Composition API).
- **Công cụ Build nhanh:** Vite.
- **Thư viện Giao diện:** Vant UI (Phiên bản 4 - Tối ưu Mobile-first).
- **Tính năng mở rộng (PWA):** Đăng ký Service Worker + `manifest.json`. Khi leo dốc, mất sóng 3G/4G, App sẽ tự động hiển thị màn hình Offline và lưu tạm (cache) trạng thái của bạn thay vì báo lỗi trắng trang.

### Phía Backend (Máy chủ lõi)
- **Framework:** Python / Django 5 (Kiến trúc MTV).
- **Xây dựng API (Backend-for-Frontend):** Django REST Framework (DRF) hỗ trợ trả data chuẩn khép kín JSON.
- **Bảo mật:** JWT Authentication chia rẽ phiên Đăng nhập giữa App và Admin.
- **Bản đồ GIS:** Thuật toán hình cầu không gian Haversine tối ưu hóa khoảng cách từ 2 tọa độ Lat-Lon.

### Lõi AI (AI Engine)
- Tích hợp 2 nhánh Model chính thức của Google:
  1. `gemini-2.0-flash`: Chẩn đoán Vision Image kèm Google Search.
  2. `gemini-2.5-flash`: Đọc hiểu file Âm thanh Gốc, bắt sóng âm cơ khí cực nhỏ trộn lẫn (Ví dụ: lột dên, kêu cò).
- **Tham số Kỹ thuật Parameter:** `temperature=0` (0% tính sáng tạo ảo tưởng), `top_k=1` (Sinh từ cứng xác suất cao nhất) giúp AI không nói linh tinh mà bám sát luật chuyên ngành Thợ nội địa Việt.

---

## 📂 Giải thích Cấu trúc Hệ thống (Directory Tree)

Dưới đây là cây thư mục toàn bộ dự án giúp Giảng viên (và Lập trình viên tiếp nhận lại) lập tức biết File nào nằm ở đâu, phụ trách logic gì:

```text
📦 DOAN2
 ┣ 📂 backend/               # [MÁY CHỦ] Toàn bộ mã nguồn API và AI Model
 ┃ ┣ 📂 apps/                # Chia nhỏ các Module Nghiệp vụ (App trong Django)
 ┃ ┃ ┣ 📂 ai_engine/         # 🧠 Lõi AI: Gắn API Google Gemini phân tích lỗi xe
 ┃ ┃ ┃ ┣ 📜 analyze_sound.py # Thuật toán xử lý file .webm/.mp3, bộ lệnh ép AI đọc tiếng máy cộc cộc
 ┃ ┃ ┃ ┣ 📜 views.py         # Gọi LLM Vision phân tích ảnh, lưu kết quả/thêm Fallback Model nếu lỗi mạng
 ┃ ┃ ┃ ┗ 📜 models.py        # Model AIReport (Lưu trữ chẩn đoán dạng Text nén)
 ┃ ┃ ┣ 📂 bookings/          # 🗺️ Nghiệp vụ Cứu hộ SOS Khẩn cấp
 ┃ ┃ ┃ ┣ 📜 models.py        # Lưu trữ Đơn Booking (Trạng thái Pending -> Completed), File Chat
 ┃ ┃ ┃ ┣ 📜 views.py         # 🔥 Thuật toán Haversine tìm 5 thợ rảnh gần nhất (5km), Polling GPS
 ┃ ┃ ┃ ┣ 📜 heatmap_view.py  # Xử lý tổng luồng đơn mảng trả về cho Bản đồ Nhiệt (Heatmap khu vực)
 ┃ ┃ ┃ ┗ 📜 admin.py         # Khai báo hệ thống Xử lý Khiếu nại (Complaints) giữa Thợ và Khách
 ┃ ┃ ┣ 📂 services/          # 🛠️ Nghiệp vụ Đặt lịch bảo dưỡng (Lên Gara) định kỳ
 ┃ ┃ ┃ ┣ 📜 models.py        # Model Service, Appointment và Hệ thống Review (Đánh giá từ 1-5 sao)
 ┃ ┃ ┃ ┗ 📜 revenue_view.py  # Script truy vấn cộng dồn Doanh thu thợ, Tỷ lệ hủy để ném biểu đồ Chart.js
 ┃ ┃ ┗ 📂 users/             # 👥 Hệ thống Quản lý Tài khoản Khách & Thợ
 ┃ ┃   ┣ 📜 models.py        # Mapping 1-1 bảng CustomUser (Khách) và MechanicProfile (Thợ - Vị trí, Số TK)
 ┃ ┃   ┗ 📜 admin.py         # Lệnh Proxy Model để vẽ ra Bảng Xếp Hạng Hiệu Suất Thợ trong Dashboard
 ┃ ┣ 📂 core/                # Thiết lập nền Backend (Settings mượt mà, URL căn bản)
 ┃ ┣ 📜 requirements.txt     # Danh sách các gói Thư viện (Pip) Python (GenAI, Django-Jazzmin...)
 ┃ ┗ 📜 manage.py            # File thực thi gõ lệnh (Dựng server/Migrate)
 ┃
 ┣ 📂 frontend/              # [GIAO DIỆN] Ứng dụng Website cài đặt được dạng App Mobile
 ┃ ┣ 📂 public/              # Chứa File cấu hình PWA: manifest.json, sw.js (Bắt sự kiện Offline)
 ┃ ┣ 📂 src/                 # Trái tim của Frontend
 ┃ ┃ ┣ 📂 assets/            # CSS Design (Mode Tối/Sáng thông minh), Hình SVG icon
 ┃ ┃ ┣ 📂 components/        # Các Module giao diện dùng chung (Bottom Navigation, Dialog chờ)
 ┃ ┃ ┣ 📂 router/            # Trạm kiểm soát Luồng (Ví dụ: Khách vãng lai cố vào sẽ bị đá ra trang Đăng nhập)
 ┃ ┃ ┣ 📂 store/             # Nơi chứa thông tin Cache tạm thời (Ví dụ: globalThemeState) 
 ┃ ┃ ┣ 📂 views/             # 🎨 Các Màn hình (Screens) tách rời, mỗi màn gọi riêng 1 luồng API
 ┃ ┃ ┃ ┣ 📜 BookingScreen.vue    # (Trang trung tâm) Radar Quét Thợ xung quanh + Box Nhắn Tin Trí Tuệ Nhân Tạo
 ┃ ┃ ┃ ┣ 📜 MechanicDashboard.vue# Màn hình Admin-mini của Thợ (Bật tắt định vị, Biểu đồ thống kê cá nhân)
 ┃ ┃ ┃ ┣ 📜 OfflineScreen.vue    # Giao diện Xử lý Khủng hoảng khi xe chết máy dọc đoạn đèo Mất Mạng
 ┃ ┃ ┃ ┣ 📜 LoginScreen.vue      # Chặn tài khoản ảo bằng xử lý Form Validation
 ┃ ┃ ┃ ┗ 📜 ProfileScreen.vue    # Theo dõi chỉ số đóng góp và Upload CMND cho Thợ
 ┃ ┃ ┣ 📜 App.vue            # Hạt nhân của App (Hút chung Router, Gắn sự kiện "Online", "Offline" của DOM)
 ┃ ┃ ┗ 📜 main.js            # Lệnh mồi (Vuốt qua các Plugin Axios, Vue, Vant UI)
 ┃ ┣ 📜 package.json         # Trạm phân phối Thư viện bên Node (Vant 4, Vue-router, Vite)
 ┃ ┗ 📜 vite.config.js       # Phối hợp mở Cổng Proxy gọi chui qua Port 8000 của Django chặn CORS
```

---

## 💻 Hướng Dẫn Khởi Chạy (Dành Cho Nhà Phát Triển)

Để xem đồ án chạy trực tiếp trên máy, vui lòng thực thi các lệnh sau:

### 1. Kích hoạt Backend (Python)
Mở cửa sổ Terminal (vào thư mục `backend/`):
```bash
# Tạo môi trường ảo tách biệt
python -m venv venv
# Truy cập vào môi trường ảo
venv\Scripts\activate      # Windows
source venv/bin/activate   # MacOS/Linux
# Tải Thư viện
pip install -r requirements.txt
# Gắn Database và Chạy
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
- Màn hình Máy Chủ (Admin) Django Jazzmin: `http://localhost:8000/admin/`

### 2. Kích hoạt Frontend (Vue.js)
Mở cửa sổ Terminal **THỨ 2** (vào thư mục `frontend/`):
```bash
# Tải các gói Package Node
npm install
# Bật tính năng HMR Vite Server
npm run dev
```
- Mở URL hiển thị trên Command Line (Bấm phím tắt F12 trên Chrome chuyển sang Mode Mobile "iPhone 14 PRO" để xem App đẹp nhất).

---

## 🎯 Quyền (Roles) trong dự án
1. **Khách hàng (`is_mechanic = False`):** Đăng nhập tự động bắt GPS. Gặp sự cố chỉ cần bấm gọi Thợ trên Bản đồ Radar, có trò chuyện và AI dự đoán. Có quyền Mở vé "Khiếu nại/Tố cáo" Thợ lừa đảo.
2. **Thợ sửa chữa (`MechanicProfile`):** Cứu kéo/Báo giá cho Khách thông qua SOS Tracking. Quản lý doanh số dịch vụ, lịch sử đặt cuộc hẹn theo 7 ngày. Phải cập nhật tọa độ liên tục.
3. **Quản trị viên / Admin (Nhà Đầu Tư):** Quyền lực tối thượng. Can thiệp hòa giải các khiếu nại (Complaint). Có bảng Xếp Hạng KPIs Thợ (Nhìn Dashboard biết thợ nào đang trốn việc, thợ nào hay bị hủy đơn) để dễ dàng ngắt hợp đồng.

---
> 🏆 **Đồ án Tốt Nghiệp** - Lĩnh vực Phần Mềm Hướng Dịch Vụ - Phát triển bởi **Nguyễn Văn [Tên Bạn]**! 
