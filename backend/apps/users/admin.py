from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, MechanicProfile

class MechanicProfileInline(admin.StackedInline):
    model = MechanicProfile
    can_delete = False
    verbose_name_plural = 'Mechanic Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (MechanicProfileInline,)
    list_display = ('username', 'email', 'is_mechanic', 'is_staff')
    list_filter = ('is_mechanic', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_mechanic', 'phone_number')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MechanicProfile)
