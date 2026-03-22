import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html, mark_safe
from .models import Service, Appointment, Review


# ─── Quản trị Model: Dịch vụ Bảo dưỡng Gara ──────────────────────────────────
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'mechanic', 'price_display', 'duration_minutes', 'action_buttons')
    list_display_links = ('id', 'name')
    list_filter   = ('mechanic',)
    search_fields = ('name', 'mechanic__user__username', 'description')
    ordering = ('mechanic', 'name')

    @admin.display(description='Thao tác')
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-sm btn-info" href="/admin/services/service/{}/change/"><i class="fas fa-edit"></i> Sửa</a> &nbsp;'
            '<a class="btn btn-sm btn-danger" href="/admin/services/service/{}/delete/"><i class="fas fa-trash"></i> Xóa</a>',
            obj.id, obj.id
        )

    @admin.display(description='Đơn giá')
    def price_display(self, obj):
        return f"{obj.price:,.0f} ₫" if obj.price else '—'


# ─── Hành động Tùy chỉnh: Export CSV Lịch hẹn ─────────────────
def export_appointments_csv(modeladmin, request, queryset):
    """Xuất danh sách lịch hẹn ra CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="appointments.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Khách hàng', 'Thợ', 'Dịch vụ', 'Giờ hẹn', 'Trạng thái', 'Ghi chú'])
    for a in queryset:
        writer.writerow([
            a.id, a.customer.username, a.mechanic.user.username,
            a.service.name,
            a.appointment_time.strftime('%d/%m/%Y %H:%M'),
            a.status, a.note or '—',
        ])
    return response
export_appointments_csv.short_description = 'Xuất CSV lịch hẹn đã chọn'


# ─── Quản trị Model: Lịch hẹn ──────────────────────────────
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    actions = [export_appointments_csv]
    list_display  = ('id', 'customer', 'mechanic', 'service', 'appointment_time', 'status_badge', 'payment_status', 'action_buttons')
    list_display_links = ('id', 'customer')
    list_filter  = ('status', 'payment_status', 'appointment_time')
    search_fields = ('customer__username', 'mechanic__user__username', 'service__name', 'note')
    readonly_fields = ('created_at',)
    ordering = ('-appointment_time',)
    date_hierarchy = 'appointment_time'
    list_per_page = 20

    fieldsets = (
        ('Các bên', {'fields': ('customer', 'mechanic', 'service')}),
        ('Lịch hẹn', {'fields': ('appointment_time', 'status', 'note', 'cancel_reason')}),
        ('Thanh toán', {'fields': ('payment_method', 'payment_status')}),
        ('Metadata', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    @admin.display(description='Trạng thái', ordering='status')
    def status_badge(self, obj):
        colors = {
            'PENDING':   '#ffc107',
            'CONFIRMED': '#17a2b8',
            'COMPLETED': '#28a745',
            'CANCELLED': '#dc3545',
        }
        labels = {
            'PENDING':   'Chờ xác nhận',
            'CONFIRMED': 'Đã xác nhận',
            'COMPLETED': 'Hoàn thành',
            'CANCELLED': 'Đã hủy',
        }
        color = colors.get(obj.status, '#6c757d')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:12px;font-size:11px">{}</span>',
            color, label
        )

    @admin.display(description='Thao tác')
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-sm btn-info" href="/admin/services/appointment/{}/change/"><i class="fas fa-edit"></i> Sửa</a> &nbsp;'
            '<a class="btn btn-sm btn-danger" href="/admin/services/appointment/{}/delete/"><i class="fas fa-trash"></i> Xóa</a>',
            obj.id, obj.id
        )


# ─── Custom Action: Xóa đánh giá vi phạm ───────────
def xoa_danh_gia_vi_pham(modeladmin, request, queryset):
    """Xóa đánh giá vi phạm: dưới 2 sao và không có nhận xét."""
    count = queryset.filter(rating__lte=2, comment='').count()
    queryset.filter(rating__lte=2, comment='').delete()
    modeladmin.message_user(request, f'Đã xóa {count} đánh giá vi phạm.')
xoa_danh_gia_vi_pham.short_description = 'Xóa đánh giá vi phạm (<=2 sao không có nhận xét)'


# ─── Quản trị Model: Đánh giá & Phản hồi ───────────────────────────────────
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    actions = [xoa_danh_gia_vi_pham]
    list_display  = ('id', 'customer', 'mechanic', 'star_display', 'short_comment', 'created_at', 'action_buttons')
    list_display_links = ('id', 'customer')
    list_filter   = ('rating', 'created_at')
    search_fields = ('customer__username', 'mechanic__user__username', 'comment')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    @admin.display(description='Thao tác')
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-sm btn-danger" href="/admin/services/review/{}/delete/"><i class="fas fa-trash"></i> Xóa</a>',
            obj.id
        )

    @admin.display(description='Số Sao', ordering='rating')
    def star_display(self, obj):
        stars = '<i class="fas fa-star"></i>' * obj.rating + '<i class="far fa-star"></i>' * (5 - obj.rating)
        color = '#28a745' if obj.rating >= 4 else ('#ffc107' if obj.rating == 3 else '#dc3545')
        # Truyền color và stars như args để tuân thủ Django 6.x
        return format_html('<span style="color:{}">{}</span>', color, mark_safe(stars))

    @admin.display(description='Nhận xét')
    def short_comment(self, obj):
        if not obj.comment:
            # Dùng format_html với placeholder {} để có args
            return format_html('<em style="color:#6c757d">{}</em>', 'Không có nhận xét')
        return (obj.comment[:70] + '…') if len(obj.comment) > 70 else obj.comment
