"""
Utility functions for sending push notifications.
"""

import json
import logging
from django.conf import settings
from pywebpush import webpush, WebPushException
from .models import PushSubscription

logger = logging.getLogger(__name__)


def send_push_notification(user, title, message, tag="default", icon="/icon.png", badge="/badge.png"):
    """
    Send a push notification to all active subscriptions of a user.
    
    Args:
        user: User object to send notification to
        title: Notification title
        message: Notification message/body
        tag: Notification tag for grouping
        icon: URL to notification icon
        badge: URL to notification badge
    
    Returns:
        dict: {
            'success': int (number of successful sends),
            'failed': int (number of failed sends),
            'deleted_subscriptions': int (number of deleted invalid subscriptions)
        }
    """
    
    # Build notification payload
    payload = {
        'title': title,
        'body': message,
        'icon': icon,
        'badge': badge,
        'tag': tag,
        'timestamp': int(__import__('time').time() * 1000),  # milliseconds
    }
    
    # Get all active subscriptions for user
    subscriptions = PushSubscription.objects.filter(
        user=user,
        is_active=True
    )
    
    success_count = 0
    failed_count = 0
    deleted_count = 0
    
    for subscription in subscriptions:
        try:
            subscription_object = {
                'endpoint': subscription.endpoint,
                'keys': {
                    'p256dh': subscription.p256dh,
                    'auth': subscription.auth,
                }
            }
            
            # Send the push notification
            webpush(
                subscription_info=subscription_object,
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={
                    'sub': settings.VAPID_ADMIN_EMAIL,
                }
            )
            
            success_count += 1
            logger.info(f"Push notification sent to {user.username}")
            
        except WebPushException as e:
            # Handle push service errors
            logger.error(f"WebPush error for {subscription.endpoint}: {e}")
            
            # Check if subscription is expired (410) or invalid (401, 404)
            if hasattr(e, 'status') and e.status in [401, 404, 410]:
                # Delete invalid subscription
                subscription.delete()
                deleted_count += 1
                logger.info(f"Deleted invalid subscription for {user.username}")
            else:
                failed_count += 1
                
        except Exception as e:
            failed_count += 1
            logger.error(f"Unexpected error sending push to {user.username}: {e}")
    
    return {
        'success': success_count,
        'failed': failed_count,
        'deleted_subscriptions': deleted_count,
    }


def send_push_to_users(users, title, message, **kwargs):
    """
    Send push notification to multiple users.
    
    Args:
        users: QuerySet or list of User objects
        title: Notification title
        message: Notification message
        **kwargs: Additional parameters for send_push_notification
    
    Returns:
        dict: Aggregated results
    """
    
    total_success = 0
    total_failed = 0
    total_deleted = 0
    
    for user in users:
        result = send_push_notification(user, title, message, **kwargs)
        total_success += result['success']
        total_failed += result['failed']
        total_deleted += result['deleted_subscriptions']
    
    return {
        'total_success': total_success,
        'total_failed': total_failed,
        'total_deleted_subscriptions': total_deleted,
    }


def cleanup_invalid_subscriptions(user):
    """
    Mark subscriptions as inactive without deleting them.
    Useful for keeping history of subscriptions.
    
    Args:
        user: User object
    """
    
    inactive_count = PushSubscription.objects.filter(
        user=user,
        is_active=True
    ).update(is_active=False)
    
    logger.info(f"Marked {inactive_count} subscriptions as inactive for {user.username}")
    return inactive_count
