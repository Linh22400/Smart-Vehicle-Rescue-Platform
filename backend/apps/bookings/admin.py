import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import Booking, ChatMessage, Complaint


# ─── Hành động Tùy chỉnh ──────────────────────────────────
def export_bookings_csv(modeladmin, request, queryset):
    """Xuất danh sách đơn SOS ra CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Khách hàng', 'Thợ', 'Trạng thái', 'Loại xe', 'Chi phí (VNĐ)', 'Thanh toán', 'Ngày tạo'])
    for b in queryset:
        writer.writerow([
            b.id, b.customer.username,
            b.mechanic.username if b.mechanic else '—',
            b.status, b.vehicle_type,
            b.repair_cost or 0, b.payment_status,
            b.created_at.strftime('%d/%m/%Y %H:%M'),
        ])
    return response
export_bookings_csv.short_description = 'Xuất CSV đơn SOS đã chọn'


# ─── Giao diện Nhúng: Chat trong đơn SOS ─────────────────────
class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('sender', 'text', 'created_at')
    fields = ('sender', 'text', 'created_at')
    can_delete = False
    max_num = 20
    verbose_name_plural = 'Lịch sử Chat'


# ─── Quản trị Model: Đơn cứu hộ SOS ─────────────────────────────────
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    inlines = [ChatMessageInline]
    actions = [export_bookings_csv]

    list_display = ('id', 'customer', 'mechanic', 'status_badge', 'vehicle_type',
                    'repair_cost', 'payment_badge', 'created_at', 'action_buttons')
    list_display_links = ('id', 'customer')
    list_filter  = ('status', 'vehicle_type', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('customer__username', 'mechanic__username', 'problem_description')
    readonly_fields = ('created_at', 'customer_lat', 'customer_lon')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20

    fieldsets = (
        ('Các bên liên quan', {
            'fields': ('customer', 'mechanic'),
        }),
        ('Thông tin Sự cố', {
            'fields': ('status', 'vehicle_type', 'problem_description', 'damage_image',
                       'customer_lat', 'customer_lon', 'cancel_reason'),
        }),
        ('Thanh toán', {
            'fields': ('repair_cost', 'payment_method', 'payment_status'),
        }),
        ('Thời gian', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Trạng thái', ordering='status')
    def status_badge(self, obj):
        colors = {
            'PENDING':     '#ffc107',
            'ACCEPTED':    '#17a2b8',
            'ON_THE_WAY':  '#007bff',
            'IN_PROGRESS': '#fd7e14',
            'COMPLETED':   '#28a745',
            'CANCELLED':   '#dc3545',
        }
        labels = {
            'PENDING':     'Chờ xác nhận',
            'ACCEPTED':    'Đã nhận',
            'ON_THE_WAY':  'Đang đến',
            'IN_PROGRESS': 'Đang sửa',
            'COMPLETED':   'Hoàn thành',
            'CANCELLED':   'Đã hủy',
        }
        color = colors.get(obj.status, '#6c757d')
        label = labels.get(obj.status, obj.status)
        # Truyền color và label như args để tuân thủ Django 6.x
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;border-radius:12px;font-size:11px">{}</span>',
            color, label
        )

    @admin.display(description='Thanh toán', ordering='payment_status')
    def payment_badge(self, obj):
        styles = {
            'UNPAID':  ('#dc3545', 'Chưa thanh toán'),
            'PENDING': ('#ffc107', 'Chờ xác nhận'),
            'PAID':    ('#28a745', 'Đã thanh toán'),
        }
        color, label = styles.get(obj.payment_status, ('#6c757d', obj.payment_status or '—'))
        return format_html('<span style="color:{}">{}</span>', color, label)

    @admin.display(description='Thao tác')
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-sm btn-info" href="/admin/bookings/booking/{}/change/"><i class="fas fa-edit"></i> Sửa</a> &nbsp;'
            '<a class="btn btn-sm btn-danger" href="/admin/bookings/booking/{}/delete/"><i class="fas fa-trash"></i> Xóa</a>',
            obj.id, obj.id
        )


# ─── Quản trị Model: Tin nhắn Chat nội bộ ─────────────────────────────
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display  = ('id', 'booking', 'sender', 'short_text', 'created_at')
    list_filter   = ('created_at',)
    search_fields = ('sender__username', 'text', 'booking__id')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    @admin.display(description='Nội dung')
    def short_text(self, obj):
        return (obj.text[:60] + '…') if obj.text and len(obj.text) > 60 else (obj.text or '[Hình ảnh]')


# ─── Quản trị Model: Khiếu nại ───────────────────────────────
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'accused_user', 'booking_link', 'status_badge', 'created_at', 'action_buttons')
    list_display_links = ('id', 'created_by')
    actions = ['mark_as_resolved', 'mark_as_investigating']
    list_filter = ('status', 'created_at')
    search_fields = ('created_by__username', 'accused_user__username', 'reason')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Cá nhân liên quan', {
            'fields': ('created_by', 'accused_user', 'booking')
        }),
        ('Chi tiết khiếu nại', {
            'fields': ('reason', 'evidence_image', 'status')
        }),
        ('Xử lý của Admin', {
            'fields': ('admin_note',),
            'description': 'Ghi chú nội bộ dành cho người quản trị khi điều tra và xử lý khiếu nại.'
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Trạng thái')
    def status_badge(self, obj):
        colors = {
            'PENDING':       '#ffc107',  # Vàng
            'INVESTIGATING': '#17a2b8',  # Xanh lam
            'RESOLVED':      '#28a745',  # Xanh lá
            'DISMISSED':     '#6c757d',  # Xám
        }
        labels = {
            'PENDING':       'Chờ xử lý',
            'INVESTIGATING': 'Đang điều tra',
            'RESOLVED':      'Đã giải quyết',
            'DISMISSED':     'Từ chối',
        }
        color = colors.get(obj.status, '#333')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:12px;font-size:11px;font-weight:bold;">{}</span>',
            color, label
        )

    @admin.display(description='Đơn liên quan')
    def booking_link(self, obj):
        if obj.booking:
            return format_html('<a href="/admin/bookings/booking/{}/change/">Đơn #{}</a>', obj.booking.id, obj.booking.id)
        return '—'

    @admin.action(description="Đánh dấu: Đã giải quyết")
    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='RESOLVED')
        self.message_user(request, f'Đã đánh dấu {updated} khiếu nại thành Đã giải quyết.')

    @admin.action(description="Đánh dấu: Đang điều tra")
    def mark_as_investigating(self, request, queryset):
        updated = queryset.update(status='INVESTIGATING')
        self.message_user(request, f'Đã chuyển {updated} khiếu nại sang Trạng thái Đang điều tra.')

    @admin.display(description='Thao tác')
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-sm btn-info" href="/admin/bookings/complaint/{}/change/"><i class="fas fa-edit"></i> Xử lý</a> &nbsp;'
            '<a class="btn btn-sm btn-danger" href="/admin/bookings/complaint/{}/delete/"><i class="fas fa-trash"></i> Xóa</a>',
            obj.id, obj.id
        )

