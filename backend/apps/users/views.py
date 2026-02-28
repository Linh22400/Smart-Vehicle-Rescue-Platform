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
    """Get current user's full profile data."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        """Update phone_number and email."""
        user = request.user
        if 'phone_number' in request.data:
            user.phone_number = request.data['phone_number']
        if 'email' in request.data:
            user.email = request.data['email']
        user.save()
        return Response(UserSerializer(user).data)
