from django.urls import path
from .views import ApplyLeaveView, ApprovedLeaveListView, EmployeeLeaveHistoryView, LeaveApprovalListView, ProcessLeaveView, EmployeeLeaveBalanceView

urlpatterns = [
    
    path('apply/', ApplyLeaveView.as_view(), name='apply_leave'),
    path('history/', EmployeeLeaveHistoryView.as_view(), name='leave_history'),
    path('balance/', EmployeeLeaveBalanceView.as_view(), name='leave_balance'),
    path('manager/pending-leaves/', LeaveApprovalListView.as_view(), name='pending_leaves'),
    path('manager/process-leave/<int:pk>/', ProcessLeaveView.as_view(), name='process_leave'),
    path('manager/approved-leaves/', ApprovedLeaveListView.as_view(), name='approved_leaves'),
]
