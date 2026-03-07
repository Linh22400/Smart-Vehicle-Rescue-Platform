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
    
    # Location where the customer requested help
    customer_lat = models.FloatField()
    customer_lon = models.FloatField()
    
    problem_description = models.TextField(blank=True)

    # Payment fields
    repair_cost = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, help_text='Chi phí sửa chữa (VNĐ)')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, blank=True, default='')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='UNPAID')
    cancel_reason = models.TextField(blank=True, default='', help_text='Lý do hủy đơn')
    damage_image = models.ImageField(upload_to='sos_images/', blank=True, null=True, help_text='Ảnh mức độ hư hỏng lúc gửi SOS')

    def __str__(self):
        return f"Booking {self.id} - {self.status}"


class ChatMessage(models.Model):
    """Chat message within a booking between customer and mechanic."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg #{self.id} in Booking {self.booking_id}"
