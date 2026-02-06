from django.contrib import admin
from .models import LeaveBalance, LeaveRequest

# Register your models here.

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'applied_on')
    list_filter = ('status', 'leave_type', 'employee')
    search_fields = ('employee__username', 'reason')
    ordering = ('-applied_on',)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'casual_leave', 'sick_leave', 'emergency_leave')
    search_fields = ('employee__username',)
