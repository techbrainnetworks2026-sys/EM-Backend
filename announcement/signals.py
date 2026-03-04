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



from notifications.models import Notification

@receiver(post_save, sender=Announcement)
def notify_announcement_published(sender, instance, created, **kwargs):
    """
    Send push notification and create Notification objects for all active employees 
    when announcement is created or activated.
    """
    if created or (instance.is_active and not created):
        try:
            # Get all active employees
            employees = User.objects.filter(
                is_approved=True,
                role__isnull=False  # Has a role assigned
            )

            if employees.exists():
                # 1. Create Notification objects for each employee
                notifications_to_create = [
                    Notification(
                        user=employee,
                        title="📢 Company Announcement",
                        message=instance.title,
                        notification_type='announcement'
                    ) for employee in employees
                ]
                Notification.objects.bulk_create(notifications_to_create)

                # 2. Send push notifications to all employees
                send_push_to_users(
                    users=employees,
                    title="📢 Company Announcement",
                    message=instance.title,
                    tag="announcement",
                    icon="/icons/announcement.png",
                )

                logger.info(f"Announcement notification created and sent to {employees.count()} employees")

        except Exception as e:
            logger.error(f"Error in announcement notification signal: {e}")

