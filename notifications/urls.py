from django.urls import path
from .views import (
    SubscribePushView,
    UnsubscribePushView,
    GetVAPIDPublicKeyView,
    TestPushNotificationView,
    UnreadNotificationCountView,
)

urlpatterns = [
    # Subscribe to push notifications
    path('subscribe/', SubscribePushView.as_view(), name='subscribe_push'),
    
    # Unsubscribe from push notifications
    path('unsubscribe/', UnsubscribePushView.as_view(), name='unsubscribe_push'),
    
    # Get VAPID public key (no auth required)
    path('vapid-key/', GetVAPIDPublicKeyView.as_view(), name='vapid_key'),
    
    # Get unread notification count
    path('unread-count/', UnreadNotificationCountView.as_view(), name='unread_count'),
    
    # Debug: Test push notification (admin only)
    path('test/', TestPushNotificationView.as_view(), name='test_push'),
]
