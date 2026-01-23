from django.contrib.auth import authenticate, login
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
            
        profile.save()
        return Response(MechanicProfileSerializer(profile).data)
