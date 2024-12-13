from django.test import TestCase
from django.contrib.auth.models import User
from tutorials.models import User,Notification

class NotificationModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tutor_user", email="tutor@example.com", password="Password123")
        self.notification = Notification.objects.create(
            user=self.user,
            message="You have a new inquiry",
        )

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user,
            message="Your inquiry has been responded to."
        )

        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, "Your inquiry has been responded to.")
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)

    def test_is_read_default_value(self):
        self.assertFalse(self.notification.is_read)

    def test_mark_notification_as_read(self):
        notification = Notification.objects.create(
            user=self.user,
            message="Your inquiry has been responded to."
        )

        notification.is_read = True
        notification.save()
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_str_method_returns_correct_format(self):
        expected_str = f"Notification for {self.user.username} - {self.notification.message}"
        self.assertEqual(str(self.notification), expected_str)

