from rest_framework import viewsets, permissions, status
from .models import Task
from .serializers import TaskSerializer
from django.utils import timezone
from datetime import date

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.all()
        
        if user.role != 'MANAGER':
            queryset = queryset.filter(assigned_to=user)
        
        # Add basic filtering for month and year if provided in query params
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month:
            queryset = queryset.filter(start_date__month=month)
        if year:
            queryset = queryset.filter(start_date__year=year)
            
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        # If assigned_to is not in the validated data, default to the current user
        if 'assigned_to' not in serializer.validated_data:
            serializer.save(assigned_by=user, assigned_to=user)
        else:
            serializer.save(assigned_by=user)

    def perform_update(self, serializer):
        # If status is being changed to COMPLETED, set end_date to today
        if serializer.validated_data.get('status') == 'COMPLETED':
            serializer.save(end_date=date.today())
        else:
            serializer.save()
