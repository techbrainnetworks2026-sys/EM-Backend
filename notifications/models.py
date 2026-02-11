from django.db import models
from django.conf import settings


class PushSubscription(models.Model):
    """
    Stores browser push notification subscriptions for users.
    A user can have multiple subscriptions (one per browser/device).
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
        help_text="User who subscribed to push notifications"
    )
    
    endpoint = models.URLField(
        unique=True,
        help_text="Push service endpoint URL"
    )
    
    p256dh = models.CharField(
        max_length=500,
        help_text="Diffie-Hellman public key (base64)"
    )
    
    auth = models.CharField(
        max_length=500,
        help_text="Authentication token (base64)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this subscription is active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this subscription was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last updated time"
    )
    
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="User agent of the browser that subscribed"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Push Subscriptions"
        unique_together = [['user', 'endpoint']]

    def __str__(self):
        return f"{self.user.username} - {self.endpoint[:50]}..."
