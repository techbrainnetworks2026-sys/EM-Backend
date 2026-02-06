from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Task
from datetime import date

User = get_user_model()

class TaskModelTest(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='password123',
            role='MANAGER'
        )
        self.employee = User.objects.create_user(
            username='emp1',
            email='emp1@test.com',
            password='password123',
            role='EMPLOYEE'
        )

    def test_task_creation(self):
        task = Task.objects.create(
            title='New Task',
            description='Do something',
            assigned_to=self.employee,
            assigned_by=self.manager,
            start_date=date.today(),
            end_date=date.today()
        )
        self.assertEqual(task.status, 'PENDING')
        self.assertEqual(str(task), f"New Task - emp1")

class TaskAPITest(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager2',
            email='manager2@test.com',
            password='password123',
            role='MANAGER',
            is_approved=True
        )
        self.employee = User.objects.create_user(
            username='emp2',
            email='emp2@test.com',
            password='password123',
            role='EMPLOYEE',
            is_approved=True
        )
        self.list_url = reverse('task-list')

    def test_manager_creates_task_for_employee(self):
        self.client.force_authenticate(user=self.manager)
        data = {
            'title': 'Assigned Task',
            'description': 'Description',
            'assigned_to': self.employee.id,
            'start_date': str(date.today()),
            'end_date': str(date.today())
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(title='Assigned Task')
        self.assertEqual(task.assigned_to, self.employee)
        self.assertEqual(task.assigned_by, self.manager)

    def test_employee_creates_task_for_self(self):
        self.client.force_authenticate(user=self.employee)
        data = {
            'title': 'My Self Task',
            'description': 'Description',
            'start_date': str(date.today()),
            'end_date': str(date.today())
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(title='My Self Task')
        self.assertEqual(task.assigned_to, self.employee)
        self.assertEqual(task.assigned_by, self.employee)

    def test_employee_sees_only_own_tasks(self):
        # Manager task
        Task.objects.create(
            title='Other Task',
            description='Not for me',
            assigned_to=self.manager,
            assigned_by=self.manager
        )
        # Employee task
        Task.objects.create(
            title='My Task',
            description='For me',
            assigned_to=self.employee,
            assigned_by=self.employee
        )
        
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'My Task')

    def test_task_filtering_by_date(self):
        self.client.force_authenticate(user=self.manager)
        today = date.today()
        Task.objects.create(
            title='Task This Month',
            assigned_to=self.manager,
            assigned_by=self.manager,
            start_date=today
        )
        
        # Filter by current month and year
        response = self.client.get(f"{self.list_url}?month={today.month}&year={today.year}")
        self.assertEqual(len(response.data), 1)
        
        # Filter by wrong year
        response = self.client.get(f"{self.list_url}?year={today.year + 1}")
        self.assertEqual(len(response.data), 0)
