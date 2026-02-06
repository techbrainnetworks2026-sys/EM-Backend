from rest_framework import serializers
from .models import Announcement
from accounts.models import User

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'role')

class AnnouncementSerializer(serializers.ModelSerializer):
    author_details = UserSimpleSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
