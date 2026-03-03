from django.db import models
from django.conf import settings


class AIReport(models.Model):
    """
    Stores AI diagnosis results (text only – no image files to keep DB lightweight).
    Each report takes < 2KB, so even 100,000 reports = ~200MB max.
    Auto-cleanup removes reports older than 60 days to keep storage manageable.
    """
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_reports',
        null=True, blank=True  # Allow anonymous analyses
    )

    # ── Core diagnosis ──
    diagnosis          = models.TextField()
    severity           = models.CharField(max_length=30)
    details            = models.TextField(blank=True)

    # ── Itemised pricing (new) ──
    parts_cost         = models.CharField(max_length=150, blank=True)   # "Linh kiện: X – Y VNĐ"
    labor_cost         = models.CharField(max_length=150, blank=True)   # "Công thợ: X – Y VNĐ"
    estimated_price    = models.CharField(max_length=200, blank=True)   # Tổng cộng
    price_note         = models.TextField(blank=True)                   # Ghi chú giá thị trường

    # ── Action ──
    recommended_action = models.TextField(blank=True)
    can_drive          = models.BooleanField(default=True)
    urgency_level      = models.IntegerField(default=1)
    ai_powered         = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user = self.customer.username if self.customer else 'Anonymous'
        return f"[{self.severity}] {user} – {self.diagnosis[:40]}"
