from rest_framework import serializers
from .models import Booking
from apps.users.serializers import UserSerializer

class BookingSerializer(serializers.ModelSerializer):
    mechanic_name = serializers.CharField(source='mechanic.username', read_only=True, default='')

    class Meta:
        model = Booking
        fields = ['id', 'customer', 'mechanic', 'mechanic_name', 'status', 'created_at', 'customer_lat', 'customer_lon', 'problem_description']
        read_only_fields = ('customer', 'status', 'created_at')

class MechanicDistanceSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    distance_km = serializers.FloatField()
    rating = serializers.FloatField()
    specialty = serializers.CharField()
