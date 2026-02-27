from rest_framework import serializers
from .models import LeaveRequest, LeaveBalance

class LeaveRequestSerializer(serializers.ModelSerializer):
    
    employee_name = serializers.CharField(source='employee.username', read_only=True)
    employee_id = serializers.IntegerField(source='employee.id', read_only=True)
    department = serializers.CharField(source='employee.department', read_only=True)
    action_by_name = serializers.CharField(source='action_by.username', read_only=True, allow_null=True)

    class Meta:
        model = LeaveRequest
        fields = ['id', 'employee', 'employee_id', 'employee_name', 'department', 'leave_type', 'start_date', 'end_date', 'reason', 'status', 'applied_on', 'action_by', 'action_by_name', 'action_date']
        read_only_fields = ['employee', 'status', 'applied_on', 'action_by', 'action_date'] 
        # Employee shouldn't set their own status or choose another employee

    def create(self, validated_data):
        # Automatically assign the request to the currently authenticated user
        user = self.context['request'].user
        validated_data['employee'] = user
        return super().create(validated_data)

class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = ['casual_leave', 'sick_leave', 'emergency_leave']
