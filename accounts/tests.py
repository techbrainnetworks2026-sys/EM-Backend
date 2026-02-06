from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class UserModelTest(TestCase):
    def test_manager_auto_approval(self):
        manager = User.objects.create_user(
            username='manager1',
            email='manager1@test.com',
            password='password123',
            role=User.MANAGER
        )
        self.assertTrue(manager.is_approved)

    def test_employee_default_unapproved(self):
        employee = User.objects.create_user(
            username='employee1',
            email='employee1@test.com',
            password='password123',
            role=User.EMPLOYEE
        )
        self.assertFalse(employee.is_approved)

class AccountsAPITest(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.pending_users_url = reverse('pending_users')
        
        # Create a manager for testing restricted views
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='password123',
            role=User.MANAGER
        )
        self.manager_token = Token.objects.create(user=self.manager)

        # Create an unapproved employee
        self.employee = User.objects.create_user(
            username='employee',
            email='employee@test.com',
            password='password123',
            role=User.EMPLOYEE
        )

    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'password123',
            'role': User.EMPLOYEE,
            'department': 'IT',
            'designation': 'Developer'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@test.com')
        self.assertFalse(user.is_approved)

    def test_login_unapproved_employee(self):
        data = {
            'email': 'employee@test.com',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Account not approved', response.data['error'])

    def test_login_approved_manager(self):
        data = {
            'email': 'manager@test.com',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_manager_list_pending_users(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.manager_token.key)
        response = self.client.get(self.pending_users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'employee')

    def test_manager_approve_employee(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.manager_token.key)
        approve_url = reverse('approve_user', kwargs={'pk': self.employee.pk})
        response = self.client.post(approve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if employee is now approved
        self.employee.refresh_from_db()
        self.assertTrue(self.employee.is_approved)
        
        # Now employee should be able to login
        data = {
            'email': 'employee@test.com',
            'password': 'password123'
        }
        self.client.credentials() # Clear headers
        login_response = self.client.post(self.login_url, data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_employee_cannot_access_manager_views(self):
        employee_token = Token.objects.create(user=self.employee)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + employee_token.key)
        
        response = self.client.get(self.pending_users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
