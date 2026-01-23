from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom user model to distinguish between Customer and Mechanic.
    """
    is_mechanic = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username

class MechanicProfile(models.Model):
    """
    Profile for mechanics with location and availability content.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='mechanic_profile')
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    rating = models.FloatField(default=5.0)
    specialty = models.CharField(max_length=100, default="General Repair")

    def __str__(self):
        return f"Mechanic: {self.user.username}"
