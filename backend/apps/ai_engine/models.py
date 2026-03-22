from django.db import models
from django.conf import settings


class AIReport(models.Model):
    """
    Lưu kết quả chẩn đoán AI (chỉ văn bản — không lưu file ảnh để giữ DB nhẹ).
    Mỗi bản ghi < 2KB, 100.000 bản ghi ~200MB tối đa.
    Tự động xóa báo cáo cũ hơn 60 ngày để kiểm soát dung lượng.
    """
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_reports',
        null=True, blank=True  # Cho phép chẩn đoán ẩn danh
    )

    # ── Chẩn đoán cốt lõi ──
    diagnosis          = models.TextField()
    severity           = models.CharField(max_length=30)
    details            = models.TextField(blank=True)

    # ── Báo giá chi tiết ──
    parts_cost         = models.CharField(max_length=150, blank=True)   # "Linh kiện: X – Y VNĐ"
    labor_cost         = models.CharField(max_length=150, blank=True)   # "Công thợ: X – Y VNĐ"
    estimated_price    = models.CharField(max_length=200, blank=True)   # Tổng cộng
    price_note         = models.TextField(blank=True)                   # Ghi chú giá thị trường

    # ── Hành động khuyến nghị ──
    recommended_action = models.TextField(blank=True)
    can_drive          = models.BooleanField(default=True)
    urgency_level      = models.IntegerField(default=1)
    ai_powered         = models.BooleanField(default=True)

    # ── Nguồn phân tích (image hoặc sound) ──
    SOURCE_IMAGE = 'image'
    SOURCE_SOUND = 'sound'
    SOURCE_CHOICES = [(SOURCE_IMAGE, 'Ảnh'), (SOURCE_SOUND, 'Âm thanh')]
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_IMAGE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user = self.customer.username if self.customer else 'Ẩn danh'
        return f"[{self.severity}] {user} – {self.diagnosis[:40]}"
