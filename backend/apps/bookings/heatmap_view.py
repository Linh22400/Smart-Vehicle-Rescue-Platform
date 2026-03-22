from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from .models import Booking


class HeatmapDataView(APIView):
    """
    GET /api/bookings/heatmap/
    Trả về danh sách [lat, lon, cường độ] cho các SOS đã hoàn thành, đang xử lý và đã hủy.
    Dùng cho layer heatmap Leaflet ở frontend để hiển thị vùng sự cố nóng.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Lấy các đơn đã hoàn thành, đang xử lý, và đã hủy
        bookings = Booking.objects.filter(
            status__in=['COMPLETED', 'CANCELLED', 'IN_PROGRESS']
        ).values('customer_lat', 'customer_lon', 'status')

        points = []
        for b in bookings:
            if b['customer_lat'] and b['customer_lon']:
                # Trọng số: hoàn thành = 1.0, đang xử lý = 0.7, đã hủy = 0.5
                weight = 1.0 if b['status'] == 'COMPLETED' else (0.7 if b['status'] == 'IN_PROGRESS' else 0.5)
                points.append([
                    float(b['customer_lat']),
                    float(b['customer_lon']),
                    weight
                ])

        return Response({
            'points': points,
            'total': len(points)
        })
