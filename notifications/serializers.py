from rest_framework import serializers
from .models import PushSubscription


class PushSubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for push notification subscriptions.
    Handles creation and validation of push subscriptions.
    """
    
    class Meta:
        model = PushSubscription
        fields = ['id', 'endpoint', 'p256dh', 'auth', 'is_active', 'created_at', 'user_agent']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        """
        Create or update push subscription.
        If a subscription with the same endpoint exists, update it.
        """
        user = self.context['request'].user
        endpoint = validated_data['endpoint']
        
        subscription, created = PushSubscription.objects.update_or_create(
            user=user,
            endpoint=endpoint,
            defaults={
                'p256dh': validated_data.get('p256dh'),
                'auth': validated_data.get('auth'),
                'is_active': True,
                'user_agent': validated_data.get('user_agent', ''),
            }
        )
        
        return subscription
