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
                "message": "Login successful",
                "user": UserSerializer(user).data
            })
        else:
            return Response({"error": "Invalid credentials"}, status=400)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."})

class MechanicStatusView(APIView):
    """
    Update mechanic location and availability.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_mechanic:
            return Response({"error": "Not a mechanic"}, status=400)
        
        profile = user.mechanic_profile
        data = request.data
        
        if 'latitude' in data and 'longitude' in data:
            profile.latitude = data['latitude']
            profile.longitude = data['longitude']
        
        if 'is_available' in data:
            profile.is_available = data['is_available']
        
        if 'specialty' in data:
            profile.specialty = data['specialty']
            
        profile.save()
        return Response(MechanicProfileSerializer(profile).data)

class UserProfileView(APIView):
    """Get and update current user's profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        user = request.user
        data = request.data

        # Basic fields
        for field in ('first_name', 'last_name', 'email', 'phone_number'):
            if field in data:
                setattr(user, field, data[field])

        # Password change (requires current_password)
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

        # Re-login if password changed (session-based auth)
        if new_password:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)

        serialized = UserSerializer(user).data
        return Response(serialized)

