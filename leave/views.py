from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import LeaveRequest, LeaveBalance
from .serializers import LeaveRequestSerializer, LeaveBalanceSerializer
from accounts.permissions import IsManager # Reuse existing permission

class ApplyLeaveView(generics.CreateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

class EmployeeLeaveHistoryView(generics.ListAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LeaveRequest.objects.filter(employee=self.request.user).order_by('-applied_on')

class EmployeeLeaveBalanceView(generics.RetrieveAPIView):
    serializer_class = LeaveBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Return the balance for the current user
        # Note: In a real app, we might need to handle cases where balance object doesn't exist
        obj, created = LeaveBalance.objects.get_or_create(employee=self.request.user)
        return obj

class LeaveApprovalListView(generics.ListAPIView):
    """
    Manager view to see pending leaves
    """
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        return LeaveRequest.objects.filter(status='PENDING').order_by('applied_on')

class ProcessLeaveView(APIView):
    """
    Manager view to approve/reject leave.
    Updates leave balance if approved.
    """
    permission_classes = [IsManager]

    def post(self, request, pk):
        action = request.data.get('action') # 'APPROVE' or 'REJECT'
        
        if action not in ['APPROVE', 'REJECT']:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if leave_request.status != 'PENDING':
             return Response({'error': 'Leave request is already processed'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'APPROVE':
            # Check Balance
            employee = leave_request.employee
            balance, _ = LeaveBalance.objects.get_or_create(employee=employee)
            days_requested = (leave_request.end_date - leave_request.start_date).days + 1
            if days_requested <= 0:
                 return Response({'error': 'Invalid date range'}, status=status.HTTP_400_BAD_REQUEST)

            if leave_request.leave_type == 'CASUAL':
                if balance.casual_leave >= days_requested:
                    balance.casual_leave -= days_requested
                    balance.save()
                    leave_request.status = 'APPROVED'
                else:
                    return Response({'error': 'Insufficient Casual Leave balance'}, status=status.HTTP_400_BAD_REQUEST)
            
            elif leave_request.leave_type == 'SICK':
                if balance.sick_leave >= days_requested:
                    balance.sick_leave -= days_requested
                    balance.save()
                    leave_request.status = 'APPROVED'
                else:
                    return Response({'error': 'Insufficient Sick Leave balance'}, status=status.HTTP_400_BAD_REQUEST)
                    
            elif leave_request.leave_type == 'EMERGENCY':
                 if balance.emergency_leave >= days_requested:
                    balance.emergency_leave -= days_requested
                    balance.save()
                    leave_request.status = 'APPROVED'
                 else:
                    return Response({'error': 'Insufficient Emergency Leave balance'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                 # Default fallback if unknown type
                 leave_request.status = 'APPROVED'

        else: # REJECT
            leave_request.status = 'REJECTED'
        
        leave_request.action_by = request.user
        leave_request.action_date = timezone.now()
        leave_request.save()

        return Response({'message': f'Leave request {leave_request.status.lower()} successfully.'})
    
class ApprovedLeaveListView(generics.ListAPIView):
    """
    Manager view to see approved leaves
    """
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        return LeaveRequest.objects.filter(
            status='APPROVED'
        ).order_by('-action_date')