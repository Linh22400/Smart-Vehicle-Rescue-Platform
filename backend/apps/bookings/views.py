import math
from rest_framework.views import APIView
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from apps.users.models import MechanicProfile
from .models import Booking, ChatMessage, Complaint
from .serializers import MechanicDistanceSerializer, BookingSerializer, ChatMessageSerializer, ComplaintSerializer

class SOSFindMechanicsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Gợi ý 5 thợ cứu hộ gần nhất trong bán kính 5km.
        Dữ liệu yêu cầu: { "latitude": float, "longitude": float }
        """
        try:
            cust_lat = float(request.data.get('latitude'))
            cust_lon = float(request.data.get('longitude'))
            vehicle_type = request.data.get('vehicle_type', 'BIKE')  # Mặc định xe máy
        except (TypeError, ValueError):
            return Response({"error": "Tọa độ không hợp lệ"}, status=400)

        # Công thức Haversine tính khoảng cách giữa 2 tọa độ GPS
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Bán kính Trái Đất (km)
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        # Lọc thợ đang sẵn sàng và phục vụ đúng loại xe (hoặc ALL)
        mechanics = MechanicProfile.objects.filter(is_available=True, vehicle_type__in=[vehicle_type, 'ALL'])
        results = []

        for mech in mechanics:
            if mech.latitude is not None and mech.longitude is not None:
                dist = haversine(cust_lat, cust_lon, mech.latitude, mech.longitude)
                if dist <= 5.0:  # Bán kính 5km
                    mech.distance_km = round(dist, 2)
                    results.append(mech)

        # Sắp xếp theo khoảng cách gần nhất
        results.sort(key=lambda x: x.distance_km)
        top_5 = results[:5]

        serializer = MechanicDistanceSerializer(top_5, many=True)
        return Response(serializer.data)

class CreateBookingView(generics.CreateAPIView):
    """Hỗ trợ Khách hàng tạo mới Đơn yêu cầu cứu hộ Gửi Thợ."""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        vehicle_type = self.request.data.get('vehicle_type', 'BIKE')
        serializer.save(customer=self.request.user, vehicle_type=vehicle_type)

class BookingHistoryView(generics.ListAPIView):
    """Lấy danh sách các đơn SOS mà Khách hàng đã yêu cầu xử lý từ trước đến nay."""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(customer=self.request.user).order_by('-created_at')

class MechanicBookingListView(generics.ListAPIView):
    """Liệt kê danh sách các đơn SOS mà Thợ đã tiếp nhận phục vụ."""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(mechanic=self.request.user).order_by('-created_at')

class UpdateBookingStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn"}, status=404)

        is_owner = (booking.customer == request.user)
        is_assigned_mechanic = (booking.mechanic == request.user)

        new_status = request.data.get('status')

        # Khách hàng chỉ được phép hủy đơn
        if is_owner and not is_assigned_mechanic:
            if new_status != 'CANCELLED':
                return Response({"error": "Khách chỉ được hủy đơn"}, status=403)

        # Thợ được phép đổi sang ACCEPTED, COMPLETED, CANCELLED
        elif is_assigned_mechanic:
            pass
        else:
            return Response({"error": "Không có quyền cập nhật đơn này"}, status=403)

        if new_status in ['ACCEPTED', 'ON_THE_WAY', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']:
            if new_status == 'COMPLETED':
                repair_cost = request.data.get('repair_cost')
                if repair_cost is not None:
                    booking.repair_cost = repair_cost
            if new_status == 'CANCELLED':
                cancel_reason = request.data.get('cancel_reason', '')
                booking.cancel_reason = cancel_reason
            booking.status = new_status
            booking.save()
            return Response(BookingSerializer(booking).data)

        return Response({"error": "Trạng thái không hợp lệ"}, status=400)


class BookingTrackingView(APIView):
    """
    Theo dõi luồng tọa độ liên tục (Polling) giữa vị trí của Thợ với Khách.
    Cho phép Khách hàng xem vị trí thợ đang tiến đến trên bản đồ.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn"}, status=404)

        # Chỉ khách hoặc thợ của đơn mới được xem
        if booking.customer != request.user and booking.mechanic != request.user:
            return Response({"error": "Không có quyền truy cập"}, status=403)

        mechanic_data = {"latitude": None, "longitude": None, "username": None}
        if booking.mechanic:
            try:
                profile = booking.mechanic.mechanic_profile
                mechanic_data = {
                    "latitude": profile.latitude,
                    "longitude": profile.longitude,
                    "username": booking.mechanic.username,
                }
            except Exception:
                pass

        return Response({
            "status": booking.status,
            "mechanic": mechanic_data,
            "customer": {
                "latitude": booking.customer_lat,
                "longitude": booking.customer_lon,
            },
        })


class ConfirmPaymentView(APIView):
    """Khách hàng xác nhận đã thanh toán sau khi đơn hoàn thành."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn"}, status=404)

        # Chỉ chủ đơn (khách hàng) mới được xác nhận thanh toán
        if booking.customer != request.user:
            return Response({"error": "Không có quyền"}, status=403)

        if booking.status != 'COMPLETED':
            return Response({"error": "Đơn phải hoàn thành trước khi thanh toán"}, status=400)

        if booking.payment_status == 'PAID':
            return Response({"error": "Đơn này đã được thanh toán rồi"}, status=400)

        payment_method = request.data.get('payment_method')
        if payment_method not in ['CASH', 'TRANSFER']:
            return Response({"error": "Phương thức thanh toán không hợp lệ (CASH hoặc TRANSFER)"}, status=400)

        booking.payment_method = payment_method
        booking.payment_status = 'PENDING'
        booking.save(update_fields=['payment_method', 'payment_status'])

        return Response(BookingSerializer(booking).data)

class VerifyPaymentView(APIView):
    """Thợ xác nhận đã nhận được tiền thanh toán."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn"}, status=404)

        if booking.mechanic != request.user:
            return Response({"error": "Không có quyền xác nhận thanh toán"}, status=403)

        if booking.payment_status != 'PENDING':
            return Response({"error": "Thanh toán không ở trạng thái chờ"}, status=400)

        booking.payment_status = 'PAID'
        booking.save(update_fields=['payment_status'])

        return Response(BookingSerializer(booking).data)

class RejectPaymentView(APIView):
    """Thợ từ chối thanh toán, đặt lại trạng thái về UNPAID."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn"}, status=404)

        if booking.mechanic != request.user:
            return Response({"error": "Không có quyền từ chối thanh toán"}, status=403)

        if booking.payment_status != 'PENDING':
            return Response({"error": "Thanh toán không ở trạng thái chờ"}, status=400)

        booking.payment_status = 'UNPAID'
        booking.save(update_fields=['payment_status'])

        return Response(BookingSerializer(booking).data)

class ChatListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        booking_id = self.kwargs.get('pk')
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return ChatMessage.objects.none()

        # Bảo mật: chỉ khách hoặc thợ của đơn mới xem được chat
        if booking.customer != self.request.user and booking.mechanic != self.request.user:
            return ChatMessage.objects.none()

        return booking.messages.all()

class ChatSendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = Booking.objects.get(id=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn"}, status=404)

        if booking.customer != request.user and booking.mechanic != request.user:
            return Response({"error": "Không có quyền gửi tin nhắn cho đơn này"}, status=403)

        text = request.data.get('text', '').strip()
        image = request.FILES.get('image')

        if not text and not image:
            return Response({"error": "Cần có nội dung hoặc ảnh"}, status=400)

        msg = ChatMessage.objects.create(
            booking=booking,
            sender=request.user,
            text=text,
            image=image
        )
        return Response(ChatMessageSerializer(msg).data, status=status.HTTP_201_CREATED)


class CreateComplaintView(generics.CreateAPIView):
    """
    API để Khách hàng / Thợ tạo gửi file bằng chứng khiếu nại (bị hủy kèo, thợ bỏ trốn, khách không trả tiền).
    Phương thức: POST /api/bookings/complaints/
    Tham số (Body request): booking (id), reason (nội dung), evidence_image (file upload đính kèm)
    """
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Phương thức "create" sẽ được tùy biến hoàn toàn bởi Serializer.
    # Nhiệm vụ: Tự nhận diện ID Khách hàng đang gọi, trích xuất ID người bị tố cáo từ Đơn.
