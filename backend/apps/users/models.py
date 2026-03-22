from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Model user tùy chỉnh — phân biệt Khách hàng và Thợ.
    """
    is_mechanic = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.username

class MechanicProfile(models.Model):
    """
    Hồ sơ thợ lưu vị trí GPS, trạng thái sẵn sàng và chuyên môn.
    """
    VEHICLE_CHOICES = (
        ('BIKE', 'Xe máy'),
        ('CAR', 'Ô tô'),
        ('ALL', 'Cả hai'),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='mechanic_profile')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    rating = models.FloatField(default=5.0)
    specialty = models.CharField(max_length=100, default="General Repair")
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_CHOICES, default='ALL')
    bank_name = models.CharField(max_length=50, blank=True, null=True, help_text="Tên viết tắt Ngân hàng (VD: MB, VCB)")
    bank_account_no = models.CharField(max_length=50, blank=True, null=True, help_text="Số tài khoản")
    bank_account_name = models.CharField(max_length=100, blank=True, null=True, help_text="Tên chủ tài khoản")

    def __str__(self):
        return f"Thợ: {self.user.username}"


class MechanicPerformance(MechanicProfile):
    """
    Proxy Model riêng cho Admin: Lập Bảng xếp hạng Hiệu suất Thợ.
    Cho phép gom nhóm dữ liệu ảo mà không làm tạo thêm bảng mới trong DB.
    """
    class Meta:
        proxy = True
        verbose_name = 'Hiệu suất Thợ'
        verbose_name_plural = 'Bảng Xếp Hạng Hiệu Suất'
