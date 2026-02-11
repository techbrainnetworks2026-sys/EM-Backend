from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import PushSubscription
from .serializers import PushSubscriptionSerializer
from .utils import send_push_notification
from announcement.models import Announcement
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class SubscribePushView(generics.CreateAPIView):
    """
    Endpoint for users to subscribe to push notifications.
    User must be authenticated.
    """
    serializer_class = PushSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Save subscription with user context"""
        serializer.save()

    def create(self, request, *args, **kwargs):
        """Override to return VAPID public key"""
        response = super().create(request, *args, **kwargs)
        from django.conf import settings
        response.data['vapid_public_key'] = settings.VAPID_PUBLIC_KEY
        return response


class UnsubscribePushView(APIView):
    """
    Endpoint for users to unsubscribe from push notifications.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Unsubscribe by endpoint.
        Body: {"endpoint": "https://..."}
        """
        endpoint = request.data.get('endpoint')
        
        if not endpoint:
            return Response(
                {'error': 'Endpoint required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            subscription = PushSubscription.objects.get(
                user=request.user,
                endpoint=endpoint
            )
            subscription.is_active = False
            subscription.save()
            
            return Response(
                {'message': 'Unsubscribed successfully'},
                status=status.HTTP_200_OK
            )
        except PushSubscription.DoesNotExist:
            return Response(
                {'error': 'Subscription not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class GetVAPIDPublicKeyView(APIView):
    """
    Public endpoint to get VAPID public key.
    No authentication required.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Return VAPID public key"""
        from django.conf import settings
        return Response({
            'vapid_public_key': settings.VAPID_PUBLIC_KEY
        })


class TestPushNotificationView(APIView):
    """
    Debug endpoint to send a test push notification.
    Admin only.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        """Send test notification to authenticated user"""
        user = request.user
        title = request.data.get('title', 'Test Notification')
        message = request.data.get('message', 'This is a test notification')
        
        try:
            send_push_notification(user, title, message)
            return Response(
                {'message': 'Test notification sent'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error sending test notification: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UnreadNotificationCountView(APIView):
    """
    Get count of unread notifications for authenticated user.
    Counts active announcements as unread notifications.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Return count of unread notifications"""
        try:
            # Count active announcements (treat as unread notifications)
            unread_count = Announcement.objects.filter(is_active=True).count()
            
            return Response({
                'unread_count': unread_count,
                'message': 'Notification count retrieved successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching notification count: {e}")
            return Response({
                'error': 'Failed to fetch notification count',
                'unread_count': 0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
