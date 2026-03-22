from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Service, Appointment
from apps.users.models import MechanicProfile
from .serializers import MechanicWithServicesSerializer, AppointmentSerializer, MechanicServiceSerializer

class GarageListView(generics.ListAPIView):
    """Danh sách thợ có đăng ký dịch vụ (đóng vai trò gara)."""
    serializer_class = MechanicWithServicesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Chỉ trả thợ có ít nhất 1 dịch vụ được định nghĩa
        return MechanicProfile.objects.filter(services__isnull=False).distinct()

class MechanicServiceListCreateView(generics.ListCreateAPIView):
    """Xem danh sách dịch vụ của thợ hiện tại hoặc tạo mới."""
    serializer_class = MechanicServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, 'mechanic_profile'):
            return Service.objects.none()
        return Service.objects.filter(mechanic=self.request.user.mechanic_profile)

    def perform_create(self, serializer):
        serializer.save(mechanic=self.request.user.mechanic_profile)

class MechanicServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Xem, sửa hoặc xóa một dịch vụ của thợ hiện tại."""
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
        # Kiểm tra user có phải thợ không
        if not hasattr(self.request.user, 'mechanic_profile'):
            return Appointment.objects.none()
        return Appointment.objects.filter(mechanic=self.request.user.mechanic_profile).order_by('-appointment_time')

class UpdateAppointmentStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            appt = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Không tìm thấy lịch hẹn"}, status=404)

        # Kiểm tra quyền thao tác
        is_owner = (appt.customer == request.user)
        is_mechanic = (appt.mechanic.user == request.user)

        new_status = request.data.get('status')

        # Khách chỉ được hủy lịch hẹn
        if is_owner and not is_mechanic:
            if new_status != 'CANCELLED':
                return Response({"error": "Khách chỉ được hủy lịch hẹn"}, status=403)
        elif is_mechanic:
            pass
        else:
            return Response({"error": "Không có quyền"}, status=403)

        if new_status in ['CONFIRMED', 'COMPLETED', 'CANCELLED']:
            if new_status == 'CANCELLED':
                appt.cancel_reason = request.data.get('cancel_reason', '')
            appt.status = new_status
            appt.save()
            return Response(AppointmentSerializer(appt).data)

        return Response({"error": "Trạng thái không hợp lệ"}, status=400)


class ConfirmAppointmentPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            appt = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Không tìm thấy lịch hẹn"}, status=404)

        if appt.customer != request.user:
            return Response({"error": "Không có quyền"}, status=403)

        if appt.status != 'COMPLETED':
            return Response({"error": "Lịch hẹn phải hoàn thành trước khi thanh toán"}, status=400)

        if appt.payment_status == 'PAID':
            return Response({"error": "Đã thanh toán rồi"}, status=400)

        payment_method = request.data.get('payment_method')
        if payment_method not in ['CASH', 'TRANSFER']:
            return Response({"error": "Phương thức không hợp lệ (CASH hoặc TRANSFER)"}, status=400)

        appt.payment_method = payment_method
        appt.payment_status = 'PENDING'
        appt.save(update_fields=['payment_method', 'payment_status'])

        return Response(AppointmentSerializer(appt).data)

class VerifyAppointmentPaymentView(APIView):
    """Thợ xác nhận đã nhận được tiền của lịch hẹn."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            appt = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Không tìm thấy lịch hẹn"}, status=404)

        if appt.mechanic.user != request.user:
            return Response({"error": "Không có quyền xác nhận thanh toán"}, status=403)

        if appt.payment_status != 'PENDING':
            return Response({"error": "Thanh toán không ở trạng thái chờ"}, status=400)

        appt.payment_status = 'PAID'
        appt.save(update_fields=['payment_status'])

        return Response(AppointmentSerializer(appt).data)

class RejectAppointmentPaymentView(APIView):
    """Thợ từ chối thanh toán lịch hẹn, đặt lại về UNPAID."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            appt = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Không tìm thấy lịch hẹn"}, status=404)

        if appt.mechanic.user != request.user:
            return Response({"error": "Không có quyền từ chối thanh toán"}, status=403)

        if appt.payment_status != 'PENDING':
            return Response({"error": "Thanh toán không ở trạng thái chờ"}, status=400)

        appt.payment_status = 'UNPAID'
        appt.save(update_fields=['payment_status'])

        return Response(AppointmentSerializer(appt).data)
