from django.db import models
from django.conf import settings

class Attendance(models.Model):

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances',
        help_text="Employee whose attendance is being recorded."
    )

    date = models.DateField(
        auto_now_add=True,
        help_text="Date for which this attendance record applies."
    )

    check_in = models.TimeField(
        null=True,
        blank=True,
        help_text="Time when the employee checked in."
    )

    check_out = models.TimeField(
        null=True,
        blank=True,
        help_text="Time when the employee checked out."
    )

    class Meta:
        unique_together = ('employee', 'date')  # One attendance record per employee per day

    def __str__(self):
        return f"{self.employee.username} - {self.date}"

    @property
    def status(self):
        """
        Returns the attendance status based on check-in and check-out times.
        """
        if self.check_in and self.check_out:
            return 'PRESENT'
        elif self.check_in:
            return 'ONGOING'  # Checked in but not out
        return 'ABSENT'
