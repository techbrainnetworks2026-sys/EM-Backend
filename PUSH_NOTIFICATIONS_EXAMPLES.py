"""
Push Notification Integration Examples
======================================

This file shows how to send push notifications from different parts of the application.
Import and use the `send_push_notification` function in your views/signals.
"""

from notifications.utils import send_push_notification, send_push_to_users
from django.db.models.signals import post_save
from django.dispatch import receiver


# ============================================================================
# EXAMPLE 1: Send notification when employee account is approved
# ============================================================================

from accounts.models import User

@receiver(post_save, sender=User)
def notify_user_account_approved(sender, instance, created, **kwargs):
    """
    Signal to send push notification when user's account is approved by admin.
    Add this to your accounts/signals.py
    """
    # Only send if is_approved changed from False to True
    if not created and instance.is_approved:
        # Check if previously approved (to avoid re-sending)
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if not old_instance.is_approved:  # Status changed from False to True
                send_push_notification(
                    user=instance,
                    title="Account Approved ✅",
                    message=f"Welcome {instance.username}! Your account has been approved.",
                    tag="account-approval",
                    icon="/icons/approval.png",
                )
        except User.DoesNotExist:
            pass


# ============================================================================
# EXAMPLE 2: Send notification when leave request is approved/rejected
# ============================================================================

from leave.models import LeaveRequest

@receiver(post_save, sender=LeaveRequest)
def notify_leave_request_processed(sender, instance, created, **kwargs):
    """
    Signal to send push notification when leave request is approved or rejected.
    Add this to your leave/signals.py
    """
    if not created and instance.status in ['APPROVED', 'REJECTED']:
        # Construct message
        if instance.status == 'APPROVED':
            title = "Leave Approved ✅"
            message = f"Your leave request from {instance.start_date} to {instance.end_date} has been approved."
            tag = "leave-approved"
            icon = "/icons/approved.png"
        else:
            title = "Leave Rejected ❌"
            message = f"Your leave request from {instance.start_date} to {instance.end_date} has been rejected."
            tag = "leave-rejected"
            icon = "/icons/rejected.png"

        # Send notification
        send_push_notification(
            user=instance.employee,
            title=title,
            message=message,
            tag=tag,
            icon=icon,
        )


# ============================================================================
# EXAMPLE 3: Send notification when task is assigned
# ============================================================================

from task.models import Task

@receiver(post_save, sender=Task)
def notify_task_assigned(sender, instance, created, **kwargs):
    """
    Signal to send push notification when a task is assigned to an employee.
    Add this to your task/signals.py
    """
    if created and instance.assigned_to:  # Only on creation
        send_push_notification(
            user=instance.assigned_to,
            title="New Task Assigned 📋",
            message=f"You have been assigned: {instance.title}",
            tag="task-assigned",
            icon="/icons/task.png",
        )


# ============================================================================
# EXAMPLE 4: Send announcement to all employees
# ============================================================================

from announcement.models import Announcement
from accounts.models import User

@receiver(post_save, sender=Announcement)
def notify_announcement_published(sender, instance, created, **kwargs):
    """
    Signal to send announcement notification to all active employees.
    Add this to your announcement/signals.py
    """
    if created or instance.is_active:
        # Get all active employees
        employees = User.objects.filter(is_approved=True, role='EMPLOYEE')

        # Send to all employees
        if employees.exists():
            send_push_to_users(
                users=employees,
                title=f"📢 Announcement",
                message=instance.title,
                tag="announcement",
                icon="/icons/announcement.png",
            )


# ============================================================================
# EXAMPLE 5: Manual notification in a view
# ============================================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class SendManualNotificationView(APIView):
    """
    Example view to manually send push notifications.
    """

    def post(self, request):
        """
        Body: {
            "user_id": 1,
            "title": "Custom Title",
            "message": "Custom message"
        }
        """
        user_id = request.data.get('user_id')
        title = request.data.get('title', 'Team Monitoring')
        message = request.data.get('message', 'New notification')

        try:
            user = User.objects.get(id=user_id)
            result = send_push_notification(user, title, message)

            return Response({
                'message': 'Notification sent',
                'result': result
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================================
# EXAMPLE 6: Using in management command
# ============================================================================

from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = "Send maintenance notification to all users"

    def handle(self, *args, **options):
        """
        Usage: python manage.py notify_maintenance
        """
        users = User.objects.all()

        for user in users:
            send_push_notification(
                user=user,
                title="🔧 Maintenance Alert",
                message="System maintenance will occur tonight at 10 PM UTC.",
                tag="maintenance",
                icon="/icons/maintenance.png",
            )

        self.stdout.write(
            self.style.SUCCESS(f'✅ Sent notifications to {users.count()} users')
        )


# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================
"""
1. REGISTER SIGNALS:
   - Create signals.py in each app (if not already exists)
   - Add the signal handlers above to the appropriate signals.py
   - In apps.py, override ready() method:

   ```python
   class LeaveConfig(AppConfig):
       default_auto_field = 'django.db.models.BigAutoField'
       name = 'leave'

       def ready(self):
           import leave.signals  # Register signals
   ```

2. TEST NOTIFICATIONS:
   - Use the test endpoint: POST /api/notifications/test/
   - Or call from Django shell:
     ```
     from accounts.models import User
     from notifications.utils import send_push_notification
     user = User.objects.first()
     send_push_notification(user, "Test", "This is a test")
     ```

3. PRODUCTION SETUP:
   - Generate VAPID keys (run once):
     ```
     from py_vapid import Vapid01
     vapid = Vapid01()
     vapid.generate_keys()
     print(vapid.public_key)
     print(vapid.private_key)
     ```
   - Store in environment variables:
     VAPID_PUBLIC_KEY=...
     VAPID_PRIVATE_KEY=...
     VAPID_ADMIN_EMAIL=your@email.com

4. HANDLE INVALID SUBSCRIPTIONS:
   - Invalid subscriptions are automatically deleted when webpush fails
   - Check notifications_pushsubscription table for active subscriptions
"""
