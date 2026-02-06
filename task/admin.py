from django.contrib import admin
from .models import Task

# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'assigned_by', 'status', 'priority', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'priority', 'assigned_to', 'assigned_by')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
