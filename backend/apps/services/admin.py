from django.contrib import admin
from .models import Service, Appointment

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'mechanic', 'price')
    list_filter = ('mechanic',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'mechanic', 'service', 'appointment_time', 'status')
    list_filter = ('status', 'appointment_time')
