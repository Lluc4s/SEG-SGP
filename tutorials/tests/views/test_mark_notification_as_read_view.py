from django.test import TestCase
from django.urls import reverse
from tutorials.models import Notification, User  # Replace with the correct path to your Notification model

class MarkNotificationsAsReadViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.url = reverse('mark_notifications_as_read')

        # Create test notifications for the user
        self.unread_notification_1 = Notification.objects.create(user=self.user, is_read=False)
        self.unread_notification_2 = Notification.objects.create(user=self.user, is_read=False)
        self.read_notification = Notification.objects.create(user=self.user, is_read=True)

    def test_mark_notifications_as_read(self):
        # Simulate a GET request to mark notifications as read
        response = self.client.get(self.url)

        # Verify all unread notifications are marked as read
        self.assertTrue(Notification.objects.filter(user=self.user, is_read=False).count() == 0)
        self.assertTrue(Notification.objects.filter(user=self.user, is_read=True).count() == 3)

        # Verify the redirection to the inbox
        self.assertRedirects(response, reverse('inbox'))

    def test_no_notifications_for_user(self):
        # Delete all notifications for the user
        Notification.objects.filter(user=self.user).delete()

        # Simulate a GET request
        response = self.client.get(self.url)

        # Verify no errors are raised and redirection occurs
        self.assertRedirects(response, reverse('inbox'))

    def test_unauthenticated_user_redirects_to_login(self):
        # Log out the user to simulate unauthenticated access
        self.client.logout()

        # Attempt to access the view
        response = self.client.get(self.url)
        expected_redirect = f"/?next={self.url}"  # Assuming LOGIN_URL is '/'
        self.assertRedirects(response, expected_redirect)
