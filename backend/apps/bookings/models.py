from django.db import models
from django.conf import settings

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bookings_as_customer', on_delete=models.CASCADE)
    mechanic = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bookings_as_mechanic', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Location where the customer requested help
    customer_lat = models.FloatField()
    customer_lon = models.FloatField()
    
    problem_description = models.TextField(blank=True)

    def __str__(self):
        return f"Booking {self.id} - {self.status}"
