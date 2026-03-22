from django.contrib.auth import authenticate, login, logout
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import MechanicProfile
from .serializers import UserSerializer, MechanicProfileSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({
                "message": "Đăng nhập thành công",
                "user": UserSerializer(user).data
            })
        else:
            return Response({"error": "Sai tên đăng nhập hoặc mật khẩu"}, status=400)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Đăng xuất thành công."})

class MechanicStatusView(APIView):
    """Cập nhật trạng thái sẵn sàng và thông tin ngân hàng của thợ."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_mechanic:
            return Response({"error": "Tài khoản không phải thợ"}, status=400)

        profile = user.mechanic_profile
        data = request.data

        if 'latitude' in data and 'longitude' in data:
            profile.latitude = data['latitude']
            profile.longitude = data['longitude']

        if 'is_available' in data:
            profile.is_available = data['is_available']

        if 'specialty' in data:
            profile.specialty = data['specialty']

        if 'bank_name' in data:
            profile.bank_name = data['bank_name']
        if 'bank_account_no' in data:
            profile.bank_account_no = data['bank_account_no']
        if 'bank_account_name' in data:
            profile.bank_account_name = data['bank_account_name']

        profile.save()
        return Response(MechanicProfileSerializer(profile).data)

class MechanicUpdateLocationView(APIView):
    """API gọi liên tục để đồng bộ tọa độ GPS mới nhất của Thợ lên máy chủ."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_mechanic:
            return Response({"error": "Tài khoản không phải thợ"}, status=400)

        profile = user.mechanic_profile
        data = request.data

        lat = data.get('latitude')
        lon = data.get('longitude')

        if lat is not None and lon is not None:
            profile.latitude = float(lat)
            profile.longitude = float(lon)
            profile.save(update_fields=['latitude', 'longitude'])
            return Response({"status": "Đã cập nhật vị trí"})

        return Response({"error": "Thiếu tọa độ"}, status=400)

class UserProfileView(APIView):
    """Xem chi tiết hoặc cập nhật trực tiếp hồ sơ Khách hàng/Thợ hiện tại."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        user = request.user
        data = request.data

        # Cập nhật các trường thông tin chung
        for field in ('first_name', 'last_name', 'email', 'phone_number'):
            if field in data:
                setattr(user, field, data[field])

        # Xử lý cập nhật ảnh đại diện
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']

        # Xử lý đổi mật khẩu (Bắt buộc xác thực mật khẩu cũ)
        new_password = data.get('new_password', '').strip()
        if new_password:
            current_password = data.get('current_password', '')
            if not user.check_password(current_password):
                return Response(
                    {'error': 'Mật khẩu hiện tại không đúng'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if len(new_password) < 6:
                return Response(
                    {'error': 'Mật khẩu mới phải có ít nhất 6 ký tự'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(new_password)

        user.save()

        # Cập nhật Session Login để hệ thống không đẩy người dùng ra khỏi app sau đổi mật khẩu
        if new_password:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)

        serialized = UserSerializer(user).data
        return Response(serialized)
