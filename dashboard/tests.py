from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from task.models import Task
from attendance.models import Attendance
from django.utils import timezone

User = get_user_model()

class DashboardAPITest(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager_dash',
            email='manager_dash@test.com',
            password='password123',
            role='MANAGER',
            is_approved=True
        )
        self.employee = User.objects.create_user(
            username='employee_dash',
            email='employee_dash@test.com',
            password='password123',
            role='EMPLOYEE',
            is_approved=True
        )
        self.summary_url = reverse('dashboard_summary')

    def test_employee_dashboard_access(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'EMPLOYEE')
        self.assertIn('stats', response.data)
        self.assertIn('attendance_status', response.data['stats'])

    def test_manager_dashboard_access(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'MANAGER')
        self.assertIn('stats', response.data)
        self.assertIn('pending_approvals', response.data['stats'])

    def test_unauthenticated_access(self):
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
