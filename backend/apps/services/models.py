from django.db import models
from django.conf import settings
from apps.users.models import MechanicProfile

class Service(models.Model):
    mechanic = models.ForeignKey(MechanicProfile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0) # VND, no cents
    duration_minutes = models.IntegerField(default=30)
    
    def __str__(self):
        return f"{self.name} - {self.mechanic.user.username}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Chờ xác nhận'),
        ('CONFIRMED', 'Đã xác nhận'),
        ('COMPLETED', 'Hoàn thành'),
        ('CANCELLED', 'Đã hủy'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    mechanic = models.ForeignKey(MechanicProfile, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    appointment_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appt #{self.id} - {self.customer.username} with {self.mechanic.user.username}"

class Review(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(MechanicProfile, on_delete=models.CASCADE, related_name='reviews')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, null=True, blank=True, related_name='review')
    sos_booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='review',
    )
    rating = models.IntegerField(default=5) # 1-5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate mechanic rating
        reviews = self.mechanic.reviews.all()
        avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
        self.mechanic.rating = round(avg, 1)
        self.mechanic.save()
