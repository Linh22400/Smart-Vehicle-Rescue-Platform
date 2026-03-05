from rest_framework import serializers
from .models import Booking
from apps.users.serializers import UserSerializer

class BookingSerializer(serializers.ModelSerializer):
    mechanic_name = serializers.CharField(source='mechanic.username', read_only=True, default='')
    has_sos_review = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['id', 'customer', 'mechanic', 'mechanic_name', 'has_sos_review',
                  'status', 'vehicle_type', 'created_at', 'customer_lat', 'customer_lon', 'problem_description']
        read_only_fields = ('customer', 'status', 'created_at')

    def get_has_sos_review(self, obj):
        from apps.services.models import Review
        return Review.objects.filter(sos_booking=obj).exists()


class MechanicDistanceSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    distance_km = serializers.FloatField()
    rating = serializers.FloatField()
    specialty = serializers.CharField()
    vehicle_type = serializers.CharField()
