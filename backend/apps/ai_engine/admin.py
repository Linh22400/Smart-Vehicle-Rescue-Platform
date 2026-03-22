from django.contrib import admin
from .models import AIReport

@admin.register(AIReport)
class AIReportAdmin(admin.ModelAdmin):
    # Cột hiển thị trong danh sách
    list_display = ('id', 'customer', 'diagnosis', 'severity', 'can_drive', 'urgency_level', 'source', 'created_at')
    list_filter  = ('severity', 'can_drive', 'source', 'ai_powered', 'created_at')
    search_fields = ('customer__username', 'diagnosis', 'details')
    readonly_fields = ('created_at', 'ai_powered')
    ordering = ('-urgency_level', '-created_at')

    # Nhóm các trường thành từng section hiển thị
    fieldsets = (
        ('Thông tin Khách hàng', {
            'fields': ('customer', 'source', 'ai_powered', 'created_at'),
        }),
        ('Kết quả Chẩn đoán', {
            'fields': ('diagnosis', 'severity', 'urgency_level', 'details'),
        }),
        ('Chi phí ước tính', {
            'fields': ('parts_cost', 'labor_cost', 'estimated_price', 'price_note'),
        }),
        ('Khuyến nghị An toàn', {
            'fields': ('recommended_action', 'can_drive'),
        }),
    )
