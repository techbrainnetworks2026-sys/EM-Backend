


from django.contrib import admin
from .models import Task # or Announcement if your model name is Announcement


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    # Columns shown in admin list page
    list_display = (
        'title',
        'assigned_to',
        'assigned_by',
        'status',
        'priority',
        'start_date',
        'end_date',
    )

    # Enable filtering in left sidebar
    list_filter = (
        'status',
        'priority',
        'start_date',
    )

    # Enable search box
    search_fields = (
        'title',
        'assigned_to__username',
        'assigned_by__username',
    )
