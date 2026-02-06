
from django.db import models
from django.conf import settings

class Announcement(models.Model):

    title = models.CharField(
        max_length=255,
        help_text="Enter a short, descriptive title for the announcement."
    )
    content = models.TextField(
        help_text="Write the full announcement message here."
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcements',
        help_text="User who created this announcement."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this announcement from users."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the announcement was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the announcement was last updated."
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
