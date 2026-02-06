from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Attendance
from datetime import time, timedelta

User = get_user_model()

class AttendanceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

    def test_attendance_status_property(self):
        # Test ABSENT (no check-in, though usually records aren't created without check-in)
        attendance = Attendance.objects.create(employee=self.user)
        self.assertEqual(attendance.status, 'ABSENT')

        # Test ONGOING (check-in but no check-out)
        attendance.check_in = time(9, 0)
        self.assertEqual(attendance.status, 'ONGOING')

        # Test PRESENT (both check-in and check-out)
        attendance.check_out = time(17, 0)
        self.assertEqual(attendance.status, 'PRESENT')

class AttendanceAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='emp1',
            email='emp1@test.com',
            password='password123',
            role='EMPLOYEE',
            is_approved=True
        )
        self.client.force_authenticate(user=self.user)
        
        self.check_in_url = reverse('check_in')
        self.check_out_url = reverse('check_out')
        self.history_url = reverse('attendance_history')
        self.today_url = reverse('todays_attendance')

    def test_check_in_success(self):
        response = self.client.post(self.check_in_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Checked in successfully', response.data['message'])
        
        # Verify database record
        attendance = Attendance.objects.get(employee=self.user, date=timezone.localtime().date())
        self.assertIsNotNone(attendance.check_in)

    def test_check_in_already_done(self):
        # First check-in
        self.client.post(self.check_in_url)
        # Second check-in
        response = self.client.post(self.check_in_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'You have already checked in today.')

    def test_check_out_success(self):
        # Must check-in first
        Attendance.objects.create(
            employee=self.user, 
            date=timezone.localtime().date(),
            check_in=time(9, 0)
        )
        
        response = self.client.post(self.check_out_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Checked out successfully', response.data['message'])
        
        # Verify database record
        attendance = Attendance.objects.get(employee=self.user, date=timezone.localtime().date())
        self.assertIsNotNone(attendance.check_out)

    def test_check_out_without_check_in(self):
        response = self.client.post(self.check_out_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'You have not checked in today.')

    def test_attendance_history(self):
        # Create some history
        target_date = timezone.localtime().date() - timedelta(days=1)
        Attendance.objects.create(
            employee=self.user, 
            date=target_date,
            check_in=time(9, 0),
            check_out=time(17, 0)
        )
        
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_todays_attendance_view(self):
        # Check before check-in
        response = self.client.get(self.today_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

        # Check after check-in
        self.client.post(self.check_in_url)
        response = self.client.get(self.today_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('check_in'))
