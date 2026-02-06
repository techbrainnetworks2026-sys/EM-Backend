
from django.db import models
from django.conf import settings

class Task(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    title = models.CharField(
        max_length=200,
        help_text="Task title / short summary"
    )

    description = models.TextField(
        help_text="Detailed description of the task"
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        help_text="Employee who will work on this task"
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        help_text="Manager who created this task"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Current task status"
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        help_text="Task priority level"
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Task start date"
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expected task completion date"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Task created datetime"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last updated datetime"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.assigned_to.username}"

