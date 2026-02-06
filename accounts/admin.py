from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Fields to display in the list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_approved', 'department', 'designation', 'is_staff')
    
    # Filters on the right side of the list view
    list_filter = ('role', 'is_approved', 'department', 'is_staff', 'is_superuser', 'is_active')
    
    # Fields to be used in the detail/edit view
    fieldsets = UserAdmin.fieldsets + (
        ('Employee Info', {
            'fields': ('role', 'is_approved', 'department', 'designation', 'blood_group', 'mobile_number'),
        }),
    )
    
    # Fields to be used in the creation view
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Employee Info', {
            'fields': ('role', 'department', 'designation', 'blood_group', 'mobile_number'),
        }),
    )
    
    # Search functionality
    search_fields = ('username', 'first_name', 'last_name', 'email', 'department', 'designation')
    ordering = ('username',)
