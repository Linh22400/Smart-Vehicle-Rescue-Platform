from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'mechanic', 'status', 'created_at', 'distance_km_display')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'mechanic__username')
    
    def distance_km_display(self, obj):
        # Calculate distance if needed, or just show coords
        return f"{obj.customer_lat}, {obj.customer_lon}"
    distance_km_display.short_description = "Location"
