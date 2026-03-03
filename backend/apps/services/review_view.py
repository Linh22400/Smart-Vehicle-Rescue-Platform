from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer


class CreateReviewView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        from apps.users.models import MechanicProfile

        mechanic_input  = request.data.get('mechanic')
        appointment_id  = request.data.get('appointment')
        sos_booking_id  = request.data.get('sos_booking_id')   # NEW: sent by frontend for SOS reviews

        # ── Resolve mechanic ──────────────────────────────────────
        mechanic_profile = None
        if mechanic_input:
            mechanic_profile = MechanicProfile.objects.filter(pk=mechanic_input).first()
            if mechanic_profile is None:
                mechanic_profile = MechanicProfile.objects.filter(user_id=mechanic_input).first()

        if mechanic_profile is None:
            return Response(
                {"error": "Không tìm thấy thông tin thợ. Vui lòng thử lại."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Duplicate guard ────────────────────────────────────────
        if appointment_id:
            # Maintenance appointment review — one per appointment
            if Review.objects.filter(appointment_id=appointment_id).exists():
                return Response(
                    {"error": "Đơn dịch vụ này đã được đánh giá rồi."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # SOS review — one per specific SOS booking
            if sos_booking_id and Review.objects.filter(sos_booking_id=sos_booking_id).exists():
                return Response(
                    {"error": "Chuyến cứu hộ này đã được đánh giá rồi."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # ── Build data and save ────────────────────────────────────
        data = {
            "mechanic":    mechanic_profile.pk,
            "appointment": appointment_id,
            "rating":      request.data.get("rating", 5),
            "comment":     request.data.get("comment", ""),
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(customer=request.user)

        # Link to SOS booking if provided
        if sos_booking_id:
            try:
                from apps.bookings.models import Booking
                booking = Booking.objects.get(pk=sos_booking_id)
                review.sos_booking = booking
                review.save(update_fields=['sos_booking'])
            except Exception:
                pass  # don't fail the review if booking link fails

        return Response(serializer.data, status=status.HTTP_201_CREATED)
