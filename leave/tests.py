from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import LeaveRequest, LeaveBalance
from datetime import date, timedelta

User = get_user_model()

class LeaveModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='emp1',
            email='emp1@test.com',
            password='password123',
            role='EMPLOYEE'
        )

    def test_leave_balance_created_on_user_creation(self):
        # LeaveBalance should be created via signal
        balance = LeaveBalance.objects.get(employee=self.user)
        self.assertEqual(balance.casual_leave, 12)

    def test_leave_request_creation(self):
        request = LeaveRequest.objects.create(
            employee=self.user,
            leave_type='CASUAL',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
            reason='Vacation'
        )
        self.assertEqual(request.status, 'PENDING')
        self.assertEqual(str(request), f"emp1 - CASUAL ({date.today()} to {date.today() + timedelta(days=2)})")

class LeaveAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='emp2',
            email='emp2@test.com',
            password='password123',
            role='EMPLOYEE',
            is_approved=True
        )
        self.client.force_authenticate(user=self.user)
        self.apply_url = reverse('apply_leave')
        self.history_url = reverse('leave_history')

    def test_apply_leave_success(self):
        data = {
            'leave_type': 'SICK',
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=1)),
            'reason': 'Fever'
        }
        response = self.client.post(self.apply_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LeaveRequest.objects.filter(employee=self.user).count(), 1)

    def test_leave_history_view(self):
        LeaveRequest.objects.create(
            employee=self.user,
            leave_type='CASUAL',
            start_date=date.today(),
            end_date=date.today(),
            reason='One day off'
        )
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_leave_balance(self):
        url = reverse('leave_balance')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['casual_leave'], 12)
