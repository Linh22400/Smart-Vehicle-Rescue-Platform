import math
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from apps.users.models import MechanicProfile
from .models import Booking, ChatMessage
from .serializers import MechanicDistanceSerializer, BookingSerializer, ChatMessageSerializer

class SOSFindMechanicsView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Find 5 nearest mechanics within 5km.
        Input: { "latitude": float, "longitude": float }
        """
        try:
            cust_lat = float(request.data.get('latitude'))
            cust_lon = float(request.data.get('longitude'))
            vehicle_type = request.data.get('vehicle_type', 'BIKE') # Default to BIKE if not provided
        except (TypeError, ValueError):
            return Response({"error": "Invalid coordinates"}, status=400)

        # Haversine Formula
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Earth radius in km
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        # Filter mechanics who are available AND service the requested vehicle type (or 'ALL')
        mechanics = MechanicProfile.objects.filter(is_available=True, vehicle_type__in=[vehicle_type, 'ALL'])
        results = []
        
        for mech in mechanics:
            if mech.latitude is not None and mech.longitude is not None:
                dist = haversine(cust_lat, cust_lon, mech.latitude, mech.longitude)
                if dist <= 5.0:  # 5km radius
                    # Append mech object with added distance attribute for serializer
                    mech.distance_km = round(dist, 2)
                    results.append(mech)

        # Sort by distance
        results.sort(key=lambda x: x.distance_km)
        top_5 = results[:5]
        
        serializer = MechanicDistanceSerializer(top_5, many=True)
        return Response(serializer.data)

class CreateBookingView(generics.CreateAPIView):
    """
    Actually book a specific mechanic.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated] # Keep strict for creating bookings, simpler to debug if login works

    def perform_create(self, serializer):
        vehicle_type = self.request.data.get('vehicle_type', 'BIKE')
        serializer.save(customer=self.request.user, vehicle_type=vehicle_type)

class BookingHistoryView(generics.ListAPIView):
    """
    List all bookings for the current user (Customer).
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(customer=self.request.user).order_by('-created_at')

class MechanicBookingListView(generics.ListAPIView):
    """
    List bookings assigned to the mechanic or pending near them (simplified to assigned/pending for MVP).
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return bookings where this user is the mechanic OR (MVP) just all pending for demo?
        # Better: Bookings where mechanic is THIS user.
        return Booking.objects.filter(mechanic=self.request.user).order_by('-created_at')

class UpdateBookingStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)
        # Check permissions
        print(f"DEBUG: booking.mechanic={booking.mechanic}, request.user={request.user}, ids=({getattr(booking.mechanic, 'id', None)}, {request.user.id})")
        is_owner = (booking.customer == request.user)
        is_assigned_mechanic = (booking.mechanic == request.user)

        new_status = request.data.get('status')

        # Customer can only cancel
        if is_owner and not is_assigned_mechanic:
            if new_status != 'CANCELLED':
                return Response({"error": "Customers can only cancel bookings"}, status=403)
        
        # Only assigned mechanic can accept/complete
        elif is_assigned_mechanic:
            pass # Mechanic can change to ACCEPTED, COMPLETED, CANCELLED
        else:
             return Response({"error": "Not authorized to update this booking"}, status=403)

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
        
        return Response({"error": "Invalid status"}, status=400)


class BookingTrackingView(APIView):
    """
    GET endpoint for customers to poll the real-time location of their mechanic.
    Returns mechanic & customer coordinates + current booking status.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        # Only booking owner or assigned mechanic can track
        if booking.customer != request.user and booking.mechanic != request.user:
            return Response({"error": "Not authorized"}, status=403)

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
    """
    Customer confirms payment after booking is completed.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        # Only the booking owner (customer) can confirm payment
        if booking.customer != request.user:
            return Response({"error": "Not authorized"}, status=403)

        if booking.status != 'COMPLETED':
            return Response({"error": "Booking must be completed before payment"}, status=400)

        if booking.payment_status == 'PAID':
            return Response({"error": "Đơn này đã được thanh toán rồi"}, status=400)

        payment_method = request.data.get('payment_method')
        if payment_method not in ['CASH', 'TRANSFER']:
            return Response({"error": "Invalid payment method. Use CASH or TRANSFER"}, status=400)

        booking.payment_method = payment_method
        booking.payment_status = 'PENDING'
        booking.save(update_fields=['payment_method', 'payment_status'])

        return Response(BookingSerializer(booking).data)

class VerifyPaymentView(APIView):
    """
    Mechanic verifies that payment is received.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        if booking.mechanic != request.user:
            return Response({"error": "Not authorized to verify payment for this booking"}, status=403)

        if booking.payment_status != 'PENDING':
            return Response({"error": "Booking payment is not pending"}, status=400)

        booking.payment_status = 'PAID'
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
        
        # Security: only customer or mechanic of the booking can view chats
        if booking.customer != self.request.user and booking.mechanic != self.request.user:
            return ChatMessage.objects.none()
            
        return booking.messages.all()

class ChatSendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = Booking.objects.get(id=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        if booking.customer != request.user and booking.mechanic != request.user:
            return Response({"error": "Not authorized to send message to this booking"}, status=403)

        text = request.data.get('text', '').strip()
        image = request.FILES.get('image')

        if not text and not image:
            return Response({"error": "Message text or image is required"}, status=400)

        msg = ChatMessage.objects.create(
            booking=booking,
            sender=request.user,
            text=text,
            image=image
        )
        return Response(ChatMessageSerializer(msg).data, status=status.HTTP_201_CREATED)
