from rest_framework import serializers
from .models import Booking, ChatMessage
from apps.users.serializers import UserSerializer

class BookingSerializer(serializers.ModelSerializer):
    mechanic_name = serializers.CharField(source='mechanic.username', read_only=True, default='')
    customer_name = serializers.CharField(source='customer.username', read_only=True, default='')
    has_sos_review = serializers.SerializerMethodField()
    mechanic_bank_info = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['id', 'customer', 'customer_name', 'mechanic', 'mechanic_name', 'has_sos_review', 'mechanic_bank_info',
                  'status', 'vehicle_type', 'created_at', 'customer_lat', 'customer_lon', 'problem_description',
                  'repair_cost', 'payment_method', 'payment_status', 'cancel_reason', 'damage_image']
        read_only_fields = ('customer', 'status', 'created_at')

    def get_mechanic_bank_info(self, obj):
        if obj.mechanic and hasattr(obj.mechanic, 'mechanic_profile'):
            profile = obj.mechanic.mechanic_profile
            return {
                'bank_name': profile.bank_name,
                'bank_account_no': profile.bank_account_no,
                'bank_account_name': profile.bank_account_name
            }
        return None

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


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    is_mechanic = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'booking', 'sender', 'sender_name', 'is_mechanic', 'text', 'image', 'created_at']
        read_only_fields = ['sender', 'created_at']

    def get_is_mechanic(self, obj):
        return getattr(obj.sender, 'is_mechanic', False)
