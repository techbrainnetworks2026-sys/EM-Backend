from rest_framework import serializers
from .models import Task
from accounts.models import User

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'designation')

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_details = UserSimpleSerializer(source='assigned_to', read_only=True)
    assigned_by_details = UserSimpleSerializer(source='assigned_by', read_only=True)



    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False
    )
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('assigned_by', 'created_at', 'updated_at')


