import math
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from apps.users.models import MechanicProfile
from .models import Booking
from .serializers import MechanicDistanceSerializer, BookingSerializer

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

        mechanics = MechanicProfile.objects.filter(is_available=True)
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
        serializer.save(customer=self.request.user)

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

        if new_status in ['ACCEPTED', 'COMPLETED', 'CANCELLED']:
            booking.status = new_status
            booking.save()
            return Response(BookingSerializer(booking).data)
        
        return Response({"error": "Invalid status"}, status=400)

