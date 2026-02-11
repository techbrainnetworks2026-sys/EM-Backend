"""
Signal handlers for leave app push notifications
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LeaveRequest
from notifications.utils import send_push_notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=LeaveRequest)
def notify_leave_request_processed(sender, instance, created, **kwargs):
    """
    Send push notification when leave request status changes to APPROVED or REJECTED.
    """
    if not created:  # Only on update, not creation
        # Check if status is APPROVED or REJECTED
        if instance.status in ['APPROVED', 'REJECTED']:
            try:
                # Construct message based on status
                if instance.status == 'APPROVED':
                    title = "Leave Approved ✅"
                    message = f"Your leave request ({instance.leave_type}) from {instance.start_date} has been approved!"
                    tag = "leave-approved"
                    icon = "/icons/approved.png"
                else:  # REJECTED
                    title = "Leave Rejected ❌"
                    message = f"Your leave request ({instance.leave_type}) from {instance.start_date} has been rejected."
                    tag = "leave-rejected"
                    icon = "/icons/rejected.png"

                # Send push notification
                send_push_notification(
                    user=instance.employee,
                    title=title,
                    message=message,
                    tag=tag,
                    icon=icon,
                )

                logger.info(f"Leave notification sent to {instance.employee.username} - {instance.status}")

            except Exception as e:
                logger.error(f"Error sending leave notification: {e}")
