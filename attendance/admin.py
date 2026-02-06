from django.contrib import admin
from .models import Attendance

# Register your models here.

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'get_status')
    list_filter = ('date', 'employee')
    search_fields = ('employee__username', 'employee__first_name', 'employee__last_name')
    date_hierarchy = 'date'
    ordering = ('-date', 'employee')

    def get_status(self, obj):
        return obj.status
    get_status.short_description = 'Status'
