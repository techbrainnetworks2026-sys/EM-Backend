"""
Signal handlers for announcement app push notifications
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Announcement
from accounts.models import User
from notifications.utils import send_push_to_users
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Announcement)
def notify_announcement_published(sender, instance, created, **kwargs):
    """
    Send push notification to all active employees when announcement is created or activated.
    """
    if created or (instance.is_active and not created):
        try:
            # Get all active employees
            employees = User.objects.filter(
                is_approved=True,
                role__isnull=False  # Has a role assigned
            )

            if employees.exists():
                # Send to all employees
                send_push_to_users(
                    users=employees,
                    title="📢 Company Announcement",
                    message=instance.title,
                    tag="announcement",
                    icon="/icons/announcement.png",
                )

                logger.info(f"Announcement notification sent to {employees.count()} employees")

        except Exception as e:
            logger.error(f"Error sending announcement notification: {e}")
