"""
Signal handlers for task app push notifications
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
from notifications.utils import send_push_notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Task)
def notify_task_assigned(sender, instance, created, **kwargs):
    """
    Send push notification when a task is newly assigned to an employee.
    """
    if created and instance.assigned_to:  # Only on creation and if assigned
        try:
            send_push_notification(
                user=instance.assigned_to,
                title="New Task Assigned 📋",
                message=f"Task: {instance.title} (Priority: {instance.priority})",
                tag="task-assigned",
                icon="/icons/task.png",
            )

            logger.info(f"Task notification sent to {instance.assigned_to.username} for task '{instance.title}'")

        except Exception as e:
            logger.error(f"Error sending task notification: {e}")


@receiver(post_save, sender=Task)
def notify_task_status_changed(sender, instance, created, **kwargs):
    """
    Send push notification to task creator when task status changes.
    """
    if not created and instance.assigned_by:  # Only on update
        # Check if status changed (simplified - in production, compare with old instance)
        if instance.status in ['COMPLETED', 'IN_PROGRESS']:
            try:
                status_msg = "completed" if instance.status == 'COMPLETED' else "started"
                send_push_notification(
                    user=instance.assigned_by,
                    title=f"Task Update 🔄",
                    message=f"Task '{instance.title}' has been {status_msg}",
                    tag="task-status-changed",
                    icon="/icons/task-update.png",
                )

                logger.info(f"Task status notification sent to {instance.assigned_by.username}")

            except Exception as e:
                logger.error(f"Error sending task status notification: {e}")
