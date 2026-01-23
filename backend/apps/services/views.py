from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Service, Appointment
from apps.users.models import MechanicProfile
from .serializers import MechanicWithServicesSerializer, AppointmentSerializer

class GarageListView(generics.ListAPIView):
    """
    List mechanics who offer services (acting as Garages).
    """
    serializer_class = MechanicWithServicesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return mechanics that have at least one service defined
        return MechanicProfile.objects.filter(services__isnull=False).distinct()

class CreateAppointmentView(generics.CreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class AppointmentHistoryView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Appointment.objects.filter(customer=self.request.user).order_by('-appointment_time')

class MechanicAppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Check if user is mechanic
        if not hasattr(self.request.user, 'mechanic_profile'):
            return Appointment.objects.none()
        return Appointment.objects.filter(mechanic=self.request.user.mechanic_profile).order_by('-appointment_time')

class UpdateAppointmentStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            appt = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=404)
        
        # Check permission: Only the assigned mechanic can update
        if appt.mechanic.user != request.user:
             return Response({"error": "Not authorized"}, status=403)

        new_status = request.data.get('status')
        if new_status in ['CONFIRMED', 'COMPLETED', 'CANCELLED']:
            appt.status = new_status
            appt.save()
            return Response(AppointmentSerializer(appt).data)
        
        return Response({"error": "Invalid status"}, status=400)
