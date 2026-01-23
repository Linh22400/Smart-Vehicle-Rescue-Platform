from rest_framework import serializers
from .models import CustomUser, MechanicProfile

class MechanicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MechanicProfile
        fields = ['id', 'latitude', 'longitude', 'is_available', 'rating', 'specialty']

class UserSerializer(serializers.ModelSerializer):
    mechanic_profile = MechanicProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'is_mechanic', 'phone_number', 'mechanic_profile']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data, password=password)
        if user.is_mechanic:
            MechanicProfile.objects.create(user=user)
        return user
