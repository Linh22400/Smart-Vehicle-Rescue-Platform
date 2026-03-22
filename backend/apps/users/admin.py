import csv
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
from django.utils.html import format_html, mark_safe
from django.db.models import Count, Sum, Q, Avg
from .models import CustomUser, MechanicProfile, MechanicPerformance
from apps.bookings.models import Booking
from apps.services.models import Appointment


# ─── Hành động Tùy chỉnh (Custom Actions) ────────────────────────────────
def export_users_csv(modeladmin, request, queryset):
    """Xuất danh sách người dùng ra CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Họ tên', 'Email', 'Điện thoại', 'Vai trò', 'Ngày tham gia'])
    for user in queryset:
        writer.writerow([
            user.id, user.username,
            f"{user.first_name} {user.last_name}".strip(),
            user.email, user.phone_number,
            'Thợ cứu hộ' if user.is_mechanic else 'Khách hàng',
            user.date_joined.strftime('%d/%m/%Y'),
        ])
    return response
export_users_csv.short_description = 'Xuất CSV người dùng được chọn'


def khoa_tai_khoan(modeladmin, request, queryset):
    """Vô hiệu hóa tài khoản người dùng được chọn."""
    queryset.update(is_active=False)
khoa_tai_khoan.short_description = 'Khóa tài khoản đã chọn'


def mo_khoa_tai_khoan(modeladmin, request, queryset):
    """Kích hoạt lại tài khoản người dùng được chọn."""
    queryset.update(is_active=True)
mo_khoa_tai_khoan.short_description = 'Mở khóa tài khoản đã chọn'


# ─── Giao diện Nhúng: Hồ sơ thợ ──────────────────────────────
class MechanicProfileInline(admin.StackedInline):
    model = MechanicProfile
    can_delete = False
    verbose_name_plural = 'Hồ sơ Thợ cứu hộ'
    fk_name = 'user'
    extra = 0
    fields = (
        ('is_available', 'rating'),
        ('specialty', 'vehicle_type'),
        ('latitude', 'longitude'),
        ('bank_name', 'bank_account_no', 'bank_account_name'),
    )


# ─── Quản trị Model: CustomUser ──────────────────────────────
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = (MechanicProfileInline,)
    actions = [export_users_csv, khoa_tai_khoan, mo_khoa_tai_khoan]

    list_display = ('id', 'username', 'full_name', 'email', 'phone_number', 'role_badge', 'is_active', 'date_joined', 'action_buttons')
    list_display_links = ('id', 'username')
    list_filter = ('is_mechanic', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_per_page = 20

    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin Bổ sung', {'fields': ('is_mechanic', 'phone_number', 'avatar')}),
    )

    @admin.display(description='Họ tên', ordering='first_name')
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or '—'

    @admin.display(description='Vai trò')
    def role_badge(self, obj):
        # Dùng format_html với args để tuân thủ Django 6.x
        if obj.is_mechanic:
            return format_html(
                '<span style="background:#28a745;color:white;padding:2px 8px;border-radius:12px;font-size:11px"><i class="fas fa-wrench"></i> {}</span>',
                'Thợ'
            )
        return format_html(
            '<span style="background:#007bff;color:white;padding:2px 8px;border-radius:12px;font-size:11px"><i class="fas fa-user"></i> {}</span>',
            'Khách'
        )

    @admin.display(description='Thao tác')
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-sm btn-info" href="/admin/users/customuser/{}/change/"><i class="fas fa-edit"></i> Sửa</a> &nbsp;'
            '<a class="btn btn-sm btn-danger" href="/admin/users/customuser/{}/delete/"><i class="fas fa-trash"></i> Xóa</a>',
            obj.id, obj.id
        )


# ─── Quản trị Model: MechanicProfile ─────────────────────────
@admin.register(MechanicProfile)
class MechanicProfileAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user', 'specialty', 'vehicle_type', 'rating', 'is_available', 'has_bank_info', 'action_buttons')
    list_display_links = ('id', 'user')
    list_filter   = ('is_available', 'vehicle_type', 'specialty')
    search_fields = ('user__username', 'user__phone_number', 'specialty')
    readonly_fields = ('rating',)
    ordering = ('-rating',)

    @admin.display(description='Có TK ngân hàng', boolean=True)
    def has_bank_info(self, obj):
        return bool(obj.bank_account_no)

    @admin.display(description='Thao tác')
    def action_buttons(self, obj):
        return format_html(
            '<a class="btn btn-sm btn-info" href="/admin/users/mechanicprofile/{}/change/"><i class="fas fa-edit"></i> Sửa</a> &nbsp;'
            '<a class="btn btn-sm btn-danger" href="/admin/users/mechanicprofile/{}/delete/"><i class="fas fa-trash"></i> Xóa</a>',
            obj.id, obj.id
        )


# ─── Dashboard: Hiệu suất Thợ ───────────────────────
@admin.register(MechanicPerformance)
class MechanicPerformanceAdmin(admin.ModelAdmin):
    """Admin riêng để phân tích và đánh giá hiệu suất của Thợ."""
    
    list_display = ('user', 'rating_stars', 'completed_sos', 'completed_apps', 'total_revenue', 'cancel_rate')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    ordering = ('-rating',)
    list_per_page = 15

    # Chặn quyền Thêm, Sửa (vì đây chỉ là view thống kê)
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        """Annotate thêm dữ liệu thống kê vào queryset."""
        qs = super().get_queryset(request)
        return qs.annotate(
            completed_sos_count=Count(
                'user__bookings_as_mechanic', 
                filter=Q(user__bookings_as_mechanic__status='COMPLETED'),
                distinct=True
            ),
            cancelled_sos_count=Count(
                'user__bookings_as_mechanic', 
                filter=Q(user__bookings_as_mechanic__status='CANCELLED'),
                distinct=True
            ),
            revenue_sos=Sum(
                'user__bookings_as_mechanic__repair_cost',
                filter=Q(user__bookings_as_mechanic__status='COMPLETED')
            ),
            completed_apps_count=Count(
                'appointments',
                filter=Q(appointments__status='COMPLETED'),
                distinct=True
            )
        )

    @admin.display(description='Sao đánh giá', ordering='rating')
    def rating_stars(self, obj):
        color = '#28a745' if obj.rating >= 4.0 else ('#ffc107' if obj.rating >= 3.0 else '#dc3545')
        return format_html('<b><span style="color:{}; font-size:14px"><i class="fas fa-star"></i> {}</span></b>', color, round(obj.rating, 1))

    @admin.display(description='Đơn SOS Xong', ordering='completed_sos_count')
    def completed_sos(self, obj):
        count = getattr(obj, 'completed_sos_count', 0)
        return format_html('<b style="color:#007bff">{}</b>', count)
        
    @admin.display(description='Lịch Hẹn Xong', ordering='completed_apps_count')
    def completed_apps(self, obj):
        count = getattr(obj, 'completed_apps_count', 0)
        return format_html('<b style="color:#17a2b8">{}</b>', count)

    @admin.display(description='Tổng Doanh Thu', ordering='revenue_sos')
    def total_revenue(self, obj):
        rev = getattr(obj, 'revenue_sos', 0) or 0
        if rev == 0:
            return '—'
        formatted_rev = f"{rev:,.0f}"
        return format_html('<b style="color:#28a745">{} ₫</b>', formatted_rev)

    @admin.display(description='Tỷ lệ Hủy SOS')
    def cancel_rate(self, obj):
        comp = getattr(obj, 'completed_sos_count', 0)
        canc = getattr(obj, 'cancelled_sos_count', 0)
        total = comp + canc
        if total == 0:
            return '—'
        rate = (canc / total) * 100
        formatted_rate = f"{rate:.1f}%"
        color = '#dc3545' if rate > 30 else ('#ffc107' if rate > 10 else '#6c757d')
        return format_html('<span style="color:{}; font-weight:bold">{}</span>', color, formatted_rate)
