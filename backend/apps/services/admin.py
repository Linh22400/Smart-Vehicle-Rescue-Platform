from django.contrib import admin
from .models import Service, Appointment, Review

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'mechanic', 'price')
    list_filter = ('mechanic',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'mechanic', 'service', 'appointment_time', 'status')
    list_filter = ('status', 'appointment_time')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'mechanic', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
