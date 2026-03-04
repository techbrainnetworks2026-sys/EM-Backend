import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification
from .utils import send_push_notification

@receiver(post_save, sender=Notification)
def notify_user_on_new_notification(sender, instance, created, **kwargs):
    """
    Trigger real-time WebSocket update and push notification when a 
    new Notification object is created.
    """
    if created:
        user = instance.user
        
        # 1. Trigger WebSocket real-time update
        channel_layer = get_channel_layer()
        group_name = f"user_{user.id}"
        
        # Get current unread count
        unread_count = Notification.objects.filter(user=user, is_read=False).count()
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "data": {
                    "type": "notification_count",
                    "unread_count": unread_count,
                    "new_notification": {
                        "id": instance.id,
                        "title": instance.title,
                        "message": instance.message,
                        "notification_type": instance.notification_type,
                        "created_at": instance.created_at.isoformat()
                    }
                }
            }
        )
        
        # 2. Trigger Browser/Mobile Push Notification
        try:
            send_push_notification(
                user=user,
                title=instance.title,
                message=instance.message,
                tag=instance.notification_type
            )
        except Exception as e:
            # Log error but don't fail the signal
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send push notification: {e}")
