from rest_framework import serializers
from .models import Service, Appointment, Review
from apps.users.serializers import MechanicProfileSerializer, UserSerializer

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'duration_minutes']

class MechanicWithServicesSerializer(MechanicProfileSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta(MechanicProfileSerializer.Meta):
        fields = MechanicProfileSerializer.Meta.fields + ['services', 'user']

class AppointmentSerializer(serializers.ModelSerializer):
    service_details = ServiceSerializer(source='service', read_only=True)
    mechanic_name = serializers.CharField(source='mechanic.user.username', read_only=True)
    has_review = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = ['id', 'customer', 'mechanic', 'service', 'service_details', 'mechanic_name', 'appointment_time', 'status', 'note', 'created_at', 'has_review']
        read_only_fields = ['customer', 'status', 'created_at']

    def get_has_review(self, obj):
        return hasattr(obj, 'review')

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'customer', 'mechanic', 'appointment', 'sos_booking', 'rating', 'comment', 'created_at']
        read_only_fields = ['customer', 'created_at']
