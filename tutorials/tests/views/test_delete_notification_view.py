from django.test import TestCase
from django.urls import reverse
from tutorials.models import Notification, User  # Replace with the correct path to your Notification model

class DeleteNotificationViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        self.url = reverse('delete_notification')

        # Create a test notification for the user
        self.notification = Notification.objects.create(
            id=1,
            user=self.user,
            is_read=False,
        )

    def test_delete_existing_notification(self):
        # Simulate a POST request to delete the notification
        response = self.client.post(self.url, {'notification_id': self.notification.id})
        
        # Check if the notification was deleted
        self.assertFalse(Notification.objects.filter(id=self.notification.id).exists())
        # Assert redirection to the inbox
        self.assertRedirects(response, reverse('inbox'))

    def test_delete_nonexistent_notification(self):
        # Simulate a POST request with a non-existent notification ID
        response = self.client.post(self.url, {'notification_id': 9999})
        
        # Ensure no exception is raised and redirection happens
        self.assertRedirects(response, reverse('inbox'))

    def test_post_request_without_notification_id(self):
        # Simulate a POST request without a notification ID
        response = self.client.post(self.url)
        
        # Ensure no exceptions and redirection
        self.assertRedirects(response, reverse('inbox'))

    def test_get_request_redirects_to_inbox(self):
        # Simulate a GET request to the view
        response = self.client.get(self.url)
        
        # Ensure the response redirects to the inbox
        self.assertRedirects(response, reverse('inbox'))

    def test_unauthenticated_user_redirects_to_login(self):
        # Log out the user to simulate unauthenticated access
        self.client.logout()

        # Attempt to access the view
        response = self.client.post(self.url)
        expected_redirect = f"/?next={self.url}"  # Assuming LOGIN_URL is '/'
        self.assertRedirects(response, expected_redirect)
