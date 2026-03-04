from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User

admin.site.site_header = "EMS Administration"
admin.site.site_title = "EMS Admin Portal"
admin.site.index_title = "Welcome to EMS Dashboard"


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # Columns shown in admin list page
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_approved',
        'department',
        'designation',
        'is_staff',
        'profile_picture_preview',
    )

    # Filters on right side
    list_filter = (
        'role',
        'is_approved',
        'department',
        'is_staff',
        'is_superuser',
        'is_active',
    )

    # Fields when editing a user
    fieldsets = UserAdmin.fieldsets + (
        ('Employee Information', {
            'fields': (
                'role',
                'is_approved',
                'department',
                'designation',
                'blood_group',
                'mobile_number',
                'date_of_birth',
                'profile_picture',
            ),
        }),
    )

    # Fields when adding a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Employee Information', {
            'fields': (
                'role',
                'department',
                'designation',
                'blood_group',
                'mobile_number',
                'date_of_birth',
                'profile_picture',
            ),
        }),
    )

    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'department',
        'designation',
    )

    ordering = ('username',)

    # Profile picture preview in admin list
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius:50%;" />',
                obj.profile_picture.url
            )
        return "No Image"

    profile_picture_preview.short_description = "Profile Picture"