from django.db import models
from django.conf import settings

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('ON_THE_WAY', 'On the way'),
        ('IN_PROGRESS', 'In progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    VEHICLE_CHOICES = (
        ('BIKE', 'Xe máy'),
        ('CAR', 'Ô tô'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('CASH', 'Tiền mặt'),
        ('TRANSFER', 'Chuyển khoản'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('UNPAID', 'Chưa thanh toán'),
        ('PENDING', 'Chờ xác nhận'),
        ('PAID', 'Đã thanh toán'),
    )

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bookings_as_customer', on_delete=models.CASCADE)
    mechanic = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bookings_as_mechanic', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_CHOICES, default='BIKE')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Vị trí khách hàng gửi yêu cầu cứu hộ
    customer_lat = models.FloatField()
    customer_lon = models.FloatField()
    
    problem_description = models.TextField(blank=True)

    # Thông tin thanh toán
    repair_cost = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, help_text='Chi phí sửa chữa (VNĐ)')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, blank=True, default='')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='UNPAID')
    cancel_reason = models.TextField(blank=True, null=True, default=None, help_text='Lý do hủy đơn')
    damage_image = models.ImageField(upload_to='sos_images/', blank=True, null=True, help_text='Ảnh mức độ hư hỏng lúc gửi SOS')

    def __str__(self):
        return f"Booking {self.id} - {self.status}"


class ChatMessage(models.Model):
    """Tin nhắn chat trong đơn đặt giữa khách và thợ."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Tin #{self.id} trong Đơn {self.booking_id}"


class Complaint(models.Model):
    """
    Hệ thống xử lý khiếu nại từ khách hàng gửi về admin.
    """
    STATUS_CHOICES = (
        ('PENDING', 'Đang chờ xử lý'),
        ('INVESTIGATING', 'Đang điều tra'),
        ('RESOLVED', 'Đã giải quyết'),
        ('DISMISSED', 'Từ chối / Hủy'),
    )

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints_filed', help_text="Người tạo khiếu nại (Khách hoặc Thợ)")
    accused_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints_received', help_text="Người bị khiếu nại (Khách hoặc Thợ)")
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, help_text="Đơn cứu hộ liên quan")
    
    reason = models.TextField(help_text="Nội dung khiếu nại chi tiết")
    evidence_image = models.ImageField(upload_to='complaints/', blank=True, null=True, help_text="Ảnh bằng chứng (nếu có)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_note = models.TextField(blank=True, help_text="Ghi chú nội bộ của Admin khi xử lý")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Khiếu nại'
        verbose_name_plural = 'Quản lý Khiếu nại'

    def __str__(self):
        return f"Khiếu nại #{self.id} từ {self.created_by.username}"
