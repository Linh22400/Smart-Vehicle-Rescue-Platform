from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Service, Appointment
from apps.users.models import MechanicProfile
from .serializers import MechanicWithServicesSerializer, AppointmentSerializer, MechanicServiceSerializer

class GarageListView(generics.ListAPIView):
    """
    List mechanics who offer services (acting as Garages).
    """
    serializer_class = MechanicWithServicesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return mechanics that have at least one service defined
        # Only return mechanics that have at least one service defined
        return MechanicProfile.objects.filter(services__isnull=False).distinct()

class MechanicServiceListCreateView(generics.ListCreateAPIView):
    """
    List all services of the logged-in mechanic, or create a new service.
    """
    serializer_class = MechanicServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, 'mechanic_profile'):
            return Service.objects.none()
        return Service.objects.filter(mechanic=self.request.user.mechanic_profile)

    def perform_create(self, serializer):
        serializer.save(mechanic=self.request.user.mechanic_profile)

class MechanicServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a service for the logged-in mechanic.
    """
    serializer_class = MechanicServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, 'mechanic_profile'):
            return Service.objects.none()
        return Service.objects.filter(mechanic=self.request.user.mechanic_profile)

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
        
        # Check permission
        is_owner = (appt.customer == request.user)
        is_mechanic = (appt.mechanic.user == request.user)
        
        new_status = request.data.get('status')

        if is_owner and not is_mechanic:
            if new_status != 'CANCELLED':
                return Response({"error": "Customers can only cancel appointments"}, status=403)
        elif is_mechanic:
             pass
        else:
             return Response({"error": "Not authorized"}, status=403)

        if new_status in ['CONFIRMED', 'COMPLETED', 'CANCELLED']:
            if new_status == 'CANCELLED':
                appt.cancel_reason = request.data.get('cancel_reason', '')
            appt.status = new_status
            appt.save()
            return Response(AppointmentSerializer(appt).data)
        
        return Response({"error": "Invalid status"}, status=400)


class ConfirmAppointmentPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            appt = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=404)

        if appt.customer != request.user:
            return Response({"error": "Not authorized"}, status=403)

        if appt.status != 'COMPLETED':
            return Response({"error": "Appointment must be completed before payment"}, status=400)

        if appt.payment_status == 'PAID':
            return Response({"error": "Đã thanh toán rồi"}, status=400)

        payment_method = request.data.get('payment_method')
        if payment_method not in ['CASH', 'TRANSFER']:
            return Response({"error": "Invalid payment method"}, status=400)

        appt.payment_method = payment_method
        appt.payment_status = 'PENDING'
        appt.save(update_fields=['payment_method', 'payment_status'])

        return Response(AppointmentSerializer(appt).data)

class VerifyAppointmentPaymentView(APIView):
    """
    Mechanic verifies that appointment payment is received.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            appt = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=404)

        if appt.mechanic.user != request.user:
            return Response({"error": "Not authorized to verify payment for this appointment"}, status=403)

        if appt.payment_status != 'PENDING':
            return Response({"error": "Appointment payment is not pending"}, status=400)

        appt.payment_status = 'PAID'
        appt.save(update_fields=['payment_status'])

        return Response(AppointmentSerializer(appt).data)
