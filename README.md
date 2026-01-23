# Smart Vehicle Rescue Platform (MVP)

Hệ thống kết nối cứu hộ xe máy thông minh sử dụng Django, Vue.js và AI.

## Cấu trúc dự án
- `backend/`: Django API (User, Booking, AI Engine)
- `frontend/`: Vue 3 Client (Vante UI, Leaflet Map)

## Hướng dẫn cài đặt và chạy (Windows Powershell)

### 1. Backend (Django)
Mở một terminal tại thư mục `d:/DOAN2`:

```powershell
# Tạo venv (Optional)
python -m venv venv
.\venv\Scripts\activate

# Cài Dependencies
pip install -r requirements.txt

# Migrate Database
cd backend
python manage.py makemigrations
python manage.py migrate

# Tạo Superuser (Admin)
python manage.py createsuperuser

# Chạy Server
python manage.py runserver
```
Backend sẽ chạy tại: `http://localhost:8000`

### 2. Frontend (Vue 3)
Mở một terminal KHÁC tại `d:/DOAN2`:

```powershell
cd frontend

# Cài node modules
npm install

# Chạy Dev Server
npm run dev
```
Frontend sẽ chạy tại: `http://localhost:5173` (hoặc port hiển thị trên màn hình).

## Tính năng demo
1. **SOS Booking**: Mở web -> Click "SOS". Hệ thống sẽ lấy vị trí (hoặc mock vị trí Hà Nội) và hiển thị các thợ (MechanicProfile) trong DB.
   *Lưu ý*: Bạn cần tạo User Mechanic trong Django Admin (`http://localhost:8000/admin`) và set `is_mechanic=True`, đồng thời tạo `MechanicProfile` với tọa độ gần user (VD: Lat 21.028, Lon 105.854).
2. **AI Check**: Click "Check Hư Hỏng" -> Upload ảnh. Nếu ảnh mock (hoặc AI thật chạy) trả về kết quả.

## Admin Dashboard
Đăng nhập `http://localhost:8000/admin` để quản lý User và Booking.
