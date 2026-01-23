from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from apps.bookings.models import Booking
from apps.services.models import Appointment

class MechanicRevenueView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'mechanic_profile'):
            return Response({"error": "Not a mechanic"}, status=403)
        
        mech = request.user.mechanic_profile
        
        # 1. SOS Revenue (Assuming flat rate 150k for MVP since we didn't store price in Booking)
        sos_completed_count = Booking.objects.filter(mechanic=request.user, status='COMPLETED').count()
        sos_revenue = sos_completed_count * 150000 
        
        # 2. Services Revenue
        # Sum price of service for completed appointments
        services_stats = Appointment.objects.filter(mechanic=mech, status='COMPLETED').aggregate(
            total_revenue=Sum('service__price'),
            count=Count('id')
        )
        service_revenue = services_stats['total_revenue'] or 0
        service_count = services_stats['count'] or 0

        return Response({
            "total_revenue": sos_revenue + service_revenue,
            "sos_stats": {
                "count": sos_completed_count,
                "revenue": sos_revenue
            },
            "service_stats": {
                "count": service_count,
                "revenue": service_revenue
            }
        })
