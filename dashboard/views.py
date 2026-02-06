from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q

from accounts.models import User
from attendance.models import Attendance
from leave.models import LeaveRequest, LeaveBalance
from task.models import Task
from announcement.models import Announcement

class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localtime().date()

        if user.role == 'MANAGER':
            return self.get_manager_dashboard(user, today)
        else:
            return self.get_employee_dashboard(user, today)

    def get_employee_dashboard(self, user, today):
        # 1. Attendance Today
        attendance_today = Attendance.objects.filter(employee=user, date=today).first()
        status_today = attendance_today.status if attendance_today else 'ABSENT'

        # 2. Tasks Stats
        total_tasks = Task.objects.filter(assigned_to=user).count()
        pending_tasks = Task.objects.filter(assigned_to=user, status='PENDING').count()
        in_progress_tasks = Task.objects.filter(assigned_to=user, status='IN_PROGRESS').count()

        # 3. Leave Stats
        leave_balance = LeaveBalance.objects.filter(employee=user).first()
        pending_leaves = LeaveRequest.objects.filter(employee=user, status='PENDING').count()

        # 4. Recent Announcements
        recent_announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')[:5]
        announcement_data = [
            {
                'title': info.title,
                'created_at': info.created_at,
                'author': info.created_by.username
            } for info in recent_announcements
        ]

        # 5. Recent Tasks
        recent_tasks = Task.objects.filter(assigned_to=user).order_by('-created_at')[:5]
        task_data = [
            {
                'id': t.id,
                'title': t.title,
                'status': t.status,
                'priority': t.priority,
                'end_date': t.end_date
            } for t in recent_tasks
        ]

        return Response({
            'role': 'EMPLOYEE',
            'stats': {
                'attendance_status': status_today,
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks,
                'in_progress_tasks': in_progress_tasks,
                'pending_leaves': pending_leaves,
                'leave_balance': {
                    'casual': leave_balance.casual_leave if leave_balance else 0,
                    'sick': leave_balance.sick_leave if leave_balance else 0,
                    'emergency': leave_balance.emergency_leave if leave_balance else 0,
                }
            },
            'recent_tasks': task_data,
            'recent_announcements': announcement_data
        })

    def get_manager_dashboard(self, user, today):
        # 1. Overall Stats
        total_employees = User.objects.filter(role='EMPLOYEE').count()
        pending_approvals = User.objects.filter(role='EMPLOYEE', is_approved=False).count()
        pending_leaves = LeaveRequest.objects.filter(status='PENDING').count()
        
        present_today = Attendance.objects.filter(date=today, check_in__isnull=False).count()

        # 2. Recent Leave Requests
        recent_leaves = LeaveRequest.objects.filter(status='PENDING').order_by('-applied_on')[:5]
        leave_data = [
            {
                'id': l.id,
                'employee': l.employee.username,
                'type': l.leave_type,
                'start_date': l.start_date,
                'end_date': l.end_date,
                'reason': l.reason
            } for l in recent_leaves
        ]

        # 3. Pending User Approvals
        pending_users = User.objects.filter(role='EMPLOYEE', is_approved=False).order_by('-date_joined')[:5]
        user_data = [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'department': u.department,
                'designation': u.designation
            } for u in pending_users
        ]

        # 4. Recent Announcements
        recent_announcements = Announcement.objects.all().order_by('-created_at')[:5]
        announcement_data = [
            {
                'title': a.title,
                'is_active': a.is_active,
                'created_at': a.created_at
            } for a in recent_announcements
        ]

        # 5. Attendance Summary
        attendance_stats = Attendance.objects.filter(date=today).values('employee__department').annotate(count=Count('id'))

        return Response({
            'role': 'MANAGER',
            'stats': {
                'total_employees': total_employees,
                'pending_approvals': pending_approvals,
                'pending_leaves': pending_leaves,
                'present_today': present_today,
            },
            'pending_leave_requests': leave_data,
            'pending_user_registrations': user_data,
            'recent_announcements': announcement_data,
            'department_attendance': list(attendance_stats)
        })
