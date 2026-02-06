from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.username', read_only=True)
    status = serializers.ReadOnlyField()

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_name', 'date', 'check_in', 'check_out', 'status']
        read_only_fields = ['employee', 'date', 'check_in', 'check_out'] 
        # Times are set by actions, not direct edits usually
