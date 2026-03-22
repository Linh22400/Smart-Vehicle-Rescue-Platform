from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from apps.bookings.models import Booking
from apps.services.models import Appointment


class MechanicRevenueView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'mechanic_profile'):
            return Response({"error": "Tài khoản không phải thợ"}, status=403)

        mech = request.user.mechanic_profile
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # ── Doanh thu SOS ──
        sos_all = Booking.objects.filter(mechanic=request.user, status='COMPLETED')
        sos_stats = sos_all.aggregate(total=Sum('repair_cost'), count=Count('id'))
        sos_revenue = int(sos_stats['total'] or 0)
        sos_count = sos_stats['count'] or 0

        sos_week = sos_all.filter(created_at__gte=week_ago).aggregate(total=Sum('repair_cost'), count=Count('id'))
        sos_month = sos_all.filter(created_at__gte=month_ago).aggregate(total=Sum('repair_cost'), count=Count('id'))

        # ── Truy xuất các chỉ số Doanh thu từ Đặt lịch Bảo dưỡng Gara ──
        svc_all = Appointment.objects.filter(mechanic=mech, status='COMPLETED')
        svc_stats = svc_all.aggregate(total=Sum('service__price'), count=Count('id'))
        svc_revenue = int(svc_stats['total'] or 0)
        svc_count = svc_stats['count'] or 0

        svc_week = svc_all.filter(created_at__gte=week_ago).aggregate(total=Sum('service__price'), count=Count('id'))
        svc_month = svc_all.filter(created_at__gte=month_ago).aggregate(total=Sum('service__price'), count=Count('id'))

        # ── Thống kê hủy ──
        sos_cancelled = Booking.objects.filter(mechanic=request.user, status='CANCELLED').count()
        svc_cancelled = Appointment.objects.filter(mechanic=mech, status='CANCELLED').count()

        # ── Truy vấn Dữ liệu Doanh thu rải theo các mốc 7 ngày vẽ biểu đồ ──
        daily_labels = []
        daily_sos_revenue = []
        daily_svc_revenue = []
        daily_orders = []

        for i in range(6, -1, -1):  # Từ 6 ngày trước đến hôm nay
            day = now.date() - timedelta(days=i)
            day_start = timezone.make_aware(
                timezone.datetime.combine(day, timezone.datetime.min.time())
            )
            day_end = day_start + timedelta(days=1)

            sos_day = sos_all.filter(created_at__gte=day_start, created_at__lt=day_end).aggregate(
                total=Sum('repair_cost'), count=Count('id')
            )
            svc_day = svc_all.filter(created_at__gte=day_start, created_at__lt=day_end).aggregate(
                total=Sum('service__price'), count=Count('id')
            )
            day_label = day.strftime('%d/%m')  # Ví dụ: "08/03"
            daily_labels.append(day_label)
            daily_sos_revenue.append(int(sos_day['total'] or 0))
            daily_svc_revenue.append(int(svc_day['total'] or 0))
            daily_orders.append((sos_day['count'] or 0) + (svc_day['count'] or 0))

        # ── Phân loại trạng thái đơn cho biểu đồ Doughnut ──
        status_counts = {
            'COMPLETED':   sos_count + svc_count,
            'CANCELLED':   sos_cancelled + svc_cancelled,
            'PENDING':     Booking.objects.filter(mechanic=request.user, status='PENDING').count(),
            'IN_PROGRESS': Booking.objects.filter(mechanic=request.user, status='IN_PROGRESS').count(),
        }

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
            "rating": float(mech.rating or 0),
            # Nhóm Dữ liệu Biểu đồ Trực quan
            "chart": {
                "labels": daily_labels,
                "sos_revenue": daily_sos_revenue,
                "svc_revenue": daily_svc_revenue,
                "orders": daily_orders,
            },
            "status_breakdown": status_counts,
        })


class CustomerStatsView(APIView):
    """
    Điểm cuối API truy xuất tổng hợp tất cả giao dịch/hoạt động của Khách hàng.
    Được sử dụng trên Màn hình Profile cá nhân dạng Analytics Widgets.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        sos = Booking.objects.filter(customer=user)
        completed = sos.filter(status='COMPLETED')
        total_spent_sos = completed.aggregate(total=Sum('repair_cost'))['total'] or 0

        from apps.services.models import Appointment
        appts = Appointment.objects.filter(customer=user)
        completed_appts = appts.filter(status='COMPLETED')
        total_spent_svc = completed_appts.aggregate(total=Sum('service__price'))['total'] or 0

        return Response({
            "sos_total": sos.count(),
            "sos_completed": completed.count(),
            "sos_cancelled": sos.filter(status='CANCELLED').count(),
            "appointments_total": appts.count(),
            "appointments_completed": completed_appts.count(),
            "total_spent": int(total_spent_sos) + int(total_spent_svc),
        })
