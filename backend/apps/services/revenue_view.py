from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
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
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # SOS Revenue — real repair_cost data
        sos_all = Booking.objects.filter(mechanic=request.user, status='COMPLETED')
        sos_stats = sos_all.aggregate(total=Sum('repair_cost'), count=Count('id'))
        sos_revenue = int(sos_stats['total'] or 0)
        sos_count = sos_stats['count'] or 0

        sos_week = sos_all.filter(created_at__gte=week_ago).aggregate(total=Sum('repair_cost'), count=Count('id'))
        sos_month = sos_all.filter(created_at__gte=month_ago).aggregate(total=Sum('repair_cost'), count=Count('id'))

        # Services Revenue
        svc_all = Appointment.objects.filter(mechanic=mech, status='COMPLETED')
        svc_stats = svc_all.aggregate(total=Sum('service__price'), count=Count('id'))
        svc_revenue = int(svc_stats['total'] or 0)
        svc_count = svc_stats['count'] or 0

        svc_week = svc_all.filter(created_at__gte=week_ago).aggregate(total=Sum('service__price'), count=Count('id'))
        svc_month = svc_all.filter(created_at__gte=month_ago).aggregate(total=Sum('service__price'), count=Count('id'))

        # Cancelled stats
        sos_cancelled = Booking.objects.filter(mechanic=request.user, status='CANCELLED').count()
        svc_cancelled = Appointment.objects.filter(mechanic=mech, status='CANCELLED').count()

        return Response({
            "total_revenue": sos_revenue + svc_revenue,
            "sos_stats": {
                "count": sos_count,
                "revenue": sos_revenue,
                "week": {"count": sos_week['count'] or 0, "revenue": int(sos_week['total'] or 0)},
                "month": {"count": sos_month['count'] or 0, "revenue": int(sos_month['total'] or 0)},
            },
            "service_stats": {
                "count": svc_count,
                "revenue": svc_revenue,
                "week": {"count": svc_week['count'] or 0, "revenue": int(svc_week['total'] or 0)},
                "month": {"count": svc_month['count'] or 0, "revenue": int(svc_month['total'] or 0)},
            },
            "cancelled": sos_cancelled + svc_cancelled,
        })
