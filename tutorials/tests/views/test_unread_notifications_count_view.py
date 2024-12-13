from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from tutorials.models import Notification, User
from tutorials.views import unread_notifications_count
from django.http import HttpRequest

class UnreadNotificationsCountTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='@johndoe',
            first_name='John',
            last_name='Doe',
            email='john@john.com',
            password='Password123'
        )

    def test_unread_notifications_count_authenticated_with_unread_notifications(self):
        # Create an unread notification for the user
        Notification.objects.create(user=self.user, is_read=False)
        
        # Simulate an authenticated request
        request = HttpRequest()
        request.user = self.user
        
        # Call the unread_notifications_count function
        result = unread_notifications_count(request)
        
        # Assert that the unread notifications count is 1
        self.assertEqual(result['unread_notifications_count'], 1)

    def test_unread_notifications_count_authenticated_with_no_unread_notifications(self):
        # Create a read notification for the user (simulating no unread notifications)
        Notification.objects.create(user=self.user, is_read=True)
        
        # Simulate an authenticated request
        request = HttpRequest()
        request.user = self.user
        
        # Call the unread_notifications_count function
        result = unread_notifications_count(request)
        
        # Assert that the unread notifications count is 0
        self.assertEqual(result['unread_notifications_count'], 0)

    def test_unread_notifications_count_unauthenticated_user(self):
        # Simulate an unauthenticated request
        request = HttpRequest()
        request.user = AnonymousUser()  # This user is logged out
        
        # Call the unread_notifications_count function
        result = unread_notifications_count(request)
        
        # Assert that the unread notifications count is 0 for unauthenticated users
        self.assertEqual(result['unread_notifications_count'], 0)

    def test_unread_notifications_count_authenticated_with_multiple_notifications(self):
        # Create multiple unread notifications for the user
        Notification.objects.create(user=self.user, is_read=False)
        Notification.objects.create(user=self.user, is_read=False)
        
        # Simulate an authenticated request
        request = HttpRequest()
        request.user = self.user
        
        # Call the unread_notifications_count function
        result = unread_notifications_count(request)
        
        # Assert that the unread notifications count is 2
        self.assertEqual(result['unread_notifications_count'], 2)
