from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Announcement

User = get_user_model()

class AnnouncementModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testmanager',
            email='manager@test.com',
            password='password123',
            role='MANAGER'
        )
        self.announcement = Announcement.objects.create(
            title='Test Announcement',
            content='This is a test content',
            created_by=self.user
        )

    def test_announcement_creation(self):
        self.assertEqual(self.announcement.title, 'Test Announcement')
        self.assertEqual(self.announcement.content, 'This is a test content')
        self.assertEqual(self.announcement.created_by, self.user)
        self.assertTrue(self.announcement.is_active)

    def test_announcement_str(self):
        self.assertEqual(str(self.announcement), 'Test Announcement')

class AnnouncementAPITest(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='password123',
            role='MANAGER',
            is_staff=True # Needed for IsAdminUser permission in current ViewSet
        )
        self.employee = User.objects.create_user(
            username='employee',
            email='employee@test.com',
            password='password123',
            role='EMPLOYEE'
        )
        self.announcement = Announcement.objects.create(
            title='Public News',
            content='Everyone can see this',
            created_by=self.manager
        )
        self.list_url = reverse('announcement-list')
        self.detail_url = reverse('announcement-detail', kwargs={'pk': self.announcement.pk})

    def test_public_can_list_announcements(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the announcement is in the response
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Public News')

    def test_employee_cannot_create_announcement(self):
        self.client.force_authenticate(user=self.employee)
        data = {'title': 'Hack!', 'content': 'I am an employee'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_create_announcement(self):
        self.client.force_authenticate(user=self.manager)
        data = {'title': 'New Office', 'content': 'We are moving!'}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Announcement.objects.count(), 2)

    def test_inactive_announcements_not_listed(self):
        Announcement.objects.create(
            title='Hidden News',
            content='Shhh...',
            created_by=self.manager,
            is_active=False
        )
        response = self.client.get(self.list_url)
        # Should still only be 1 (the active one)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Public News')
