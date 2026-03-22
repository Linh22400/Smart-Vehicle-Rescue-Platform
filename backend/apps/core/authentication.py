from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Lớp cấu hình Xác thực tùy chỉnh vượt qua phần bắt lỗi CSRF.
    Được sử dụng cho Phiên bản MVP/Đồ án nhằm chia sẻ phiên đăng nhập (Session)
    giữa Admin Dashboard và Frontend Vue.js mà không cần xử lý token CSRF phức tạp.
    """
    def enforce_csrf(self, request):
        return  # Bỏ qua xác thực CSRF
