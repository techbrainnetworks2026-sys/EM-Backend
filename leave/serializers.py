from rest_framework import serializers
from django.utils import timezone
from .models import LeaveRequest, LeaveBalance

class LeaveRequestSerializer(serializers.ModelSerializer):
    
    employee_name = serializers.CharField(source='employee.username', read_only=True)
    employee_id = serializers.IntegerField(source='employee.id', read_only=True)
    department = serializers.CharField(source='employee.department', read_only=True)
    action_by_name = serializers.CharField(source='action_by.username', read_only=True, allow_null=True)

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_id', 'employee_name', 'department', 
            'leave_type', 'duration_type', 'start_date', 'end_date', 
            'from_time', 'to_time', 'total_hours', 'reason', 'status', 
            'applied_on', 'action_by', 'action_by_name', 'action_date'
        ]
        read_only_fields = ['employee', 'status', 'applied_on', 'action_by', 'action_date', 'total_hours']

    def validate(self, data):
        duration_type = data.get('duration_type', 'FULL_DAY')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        from_time = data.get('from_time')
        to_time = data.get('to_time')
        user = self.context['request'].user

        # Basic date validation
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date cannot be after end date.")

        if duration_type == 'HOURLY':
            if not from_time or not to_time:
                raise serializers.ValidationError("From time and To time are required for hourly permission.")
            
            if start_date != end_date:
                raise serializers.ValidationError("Hourly permission is only allowed for a single day.")
            
            if from_time >= to_time:
                raise serializers.ValidationError("From time must be before to time.");

            # Calculate hours
            from_datetime = timezone.datetime.combine(start_date, from_time)
            to_datetime = timezone.datetime.combine(start_date, to_time)
            diff = to_datetime - from_datetime
            hours = diff.total_seconds() / 3600

            if hours > 2:
                raise serializers.ValidationError("Maximum 2 hours allowed for hourly permission.")
            
            data['total_hours'] = hours

        elif duration_type == 'HALF_DAY':
            if start_date != end_date:
                raise serializers.ValidationError("Half day leave is only allowed for a single day.")
            data['total_hours'] = 4.0
        else:
            # Full Day
            days = (end_date - start_date).days + 1
            data['total_hours'] = days * 8.0

        # Overlap Check
        overlapping = LeaveRequest.objects.filter(
            employee=user,
            status__in=['PENDING', 'APPROVED'],
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exclude(id=self.instance.id if self.instance else None)

        if duration_type == 'HOURLY':
            # For hourly, only block if there's a full day or overlapping hourly
            for req in overlapping:
                if req.duration_type == 'FULL_DAY' or req.duration_type == 'HALF_DAY':
                    raise serializers.ValidationError(f"You already have a {req.get_duration_type_display()} request for this period.")
                
                # Check time overlap for hourly
                if req.duration_type == 'HOURLY':
                    if not (to_time <= req.from_time or from_time >= req.to_time):
                        raise serializers.ValidationError("This permission overlaps with another hourly permission.")
        else:
            # Full/Half day blocks everything in that date range
            if overlapping.exists():
                raise serializers.ValidationError("You already have a leave request that overlaps with this period.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['employee'] = user
        return super().create(validated_data)

class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = ['casual_leave', 'sick_leave', 'emergency_leave']
