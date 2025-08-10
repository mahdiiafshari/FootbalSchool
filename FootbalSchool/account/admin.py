from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ( # type: ignore
        ('Additional Info', {'fields': ('role', 'phone_number')}), )
    add_fieldsets = UserAdmin.add_fieldsets + ( #type: ignore
        ('Additional Info', {'fields': ('role', 'phone_number', 'first_name', 'last_name', 'email')}),
    )
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)