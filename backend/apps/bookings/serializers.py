from rest_framework import serializers
from .models import Booking, ChatMessage, Complaint
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


class ComplaintSerializer(serializers.ModelSerializer):
    """
    Serializer cho việc tạo và hiển thị khiếu nại (hỗ trợ cả Khách hàng và Thợ).
    """
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    accused_user_name = serializers.CharField(source='accused_user.username', read_only=True, default='')

    class Meta:
        model = Complaint
        fields = ['id', 'created_by', 'created_by_name', 'accused_user', 'accused_user_name', 'booking',
                  'reason', 'evidence_image', 'status', 'admin_note', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'status', 'admin_note', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Tự động gán created_by là người đang đăng nhập
        user = self.context['request'].user
        validated_data['created_by'] = user
        
        # Bóc tách accused_user tự động từ booking nếu có truyền booking
        booking = validated_data.get('booking')
        if booking and not validated_data.get('accused_user'):
            # Nếu người khiếu nại là Thợ -> Bị cáo là Khách hàng
            if getattr(user, 'is_mechanic', False):
                validated_data['accused_user'] = booking.customer
            # Ngược lại Khách hàng khiếu nại -> Bị cáo là Thợ
            else:
                if booking.mechanic:
                    validated_data['accused_user'] = booking.mechanic.user if hasattr(booking.mechanic, 'user') else booking.mechanic
            
        return super().create(validated_data)
