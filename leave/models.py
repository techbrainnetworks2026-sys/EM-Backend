from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class LeaveRequest(models.Model):

    items = [
        ('CASUAL', 'Casual Leave'),
        ('SICK', 'Sick Leave'),
        ('EMERGENCY', 'Emergency Leave'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_requests',
        help_text="Employee requesting the leave."
    )

    leave_type = models.CharField(
        max_length=20,
        choices=items,
        default='CASUAL',
        help_text="Type of leave being requested."
    )

    start_date = models.DateField(
        help_text="Start date of the leave."
    )

    end_date = models.DateField(
        help_text="End date of the leave."
    )

    reason = models.TextField(
        help_text="Reason for applying for leave."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Current status of the leave request."
    )

    applied_on = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the leave was applied."
    )

    # Optional: Track who approved/rejected
    action_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_leaves',
        help_text="Manager or admin who approved or rejected the leave."
    )

    action_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the leave was approved or rejected."
    )

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} ({self.start_date} to {self.end_date})"


class LeaveBalance(models.Model):

    employee = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_balance',
        help_text="Employee to whom this leave balance belongs."
    )

    casual_leave = models.IntegerField(
        default=12,
        help_text="Number of casual leave days available per year."
    )

    sick_leave = models.IntegerField(
        default=10,
        help_text="Number of sick leave days available per year."
    )

    emergency_leave = models.IntegerField(
        default=5,
        help_text="Number of emergency leave days available per year."
    )

    def __str__(self):
        return f"Balance for {self.employee.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_leave_balance(sender, instance, created, **kwargs):
    if created and instance.role == 'EMPLOYEE':
        LeaveBalance.objects.create(
            employee=instance
        )
