from django.test import TestCase
from django.contrib.auth.models import User
from tutorials.models import User,Inquiry, Notification,Tutee,Tutor

class InquiryModelTestCase(TestCase):
    def setUp(self):
        self.tutor_user = User.objects.create_user(
            username='@janedoe', email='janedoe@example.com', first_name='Jane', last_name='Doe', is_tutor=True
        )

        self.tutee_user = User.objects.create_user(
            username='@charliedoe', email='charliedoe@example.com', first_name='Charlie', last_name='Doe', is_tutor=False
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)
        self.tutee = Tutee.objects.create(user=self.tutee_user)
        self.admin = User.objects.create_user(username="admin_user", password="password123", is_staff=True)

    def test_inquiry_creation(self):
        self.inquiry = Inquiry.objects.create(
            sender=self.tutee.user,
            recipient=self.admin,
            message="I need help with my booking."
        )

        self.assertEqual(self.inquiry.sender, self.tutee.user)
        self.assertEqual(self.inquiry.recipient, self.admin)
        self.assertEqual(self.inquiry.message, "I need help with my booking.")
        self.assertEqual(self.inquiry.status, "Pending")
        self.assertIsNone(self.inquiry.response)
        self.assertIsNotNone(self.inquiry.created_at)

    def test_inquiry_response_update(self):
        self.inquiry = Inquiry.objects.create(
            sender=self.tutee.user,
            recipient=self.admin,
            message="I need help with my booking."
        )

        self.inquiry.response = "Your booking has been updated."
        self.inquiry.status = "Responded"
        self.inquiry.save()

        self.inquiry.refresh_from_db()

        self.assertEqual(self.inquiry.response, "Your booking has been updated.")
        self.assertEqual(self.inquiry.status, "Responded")

    def test_ordering_of_inquiries_and_notifications(self):
        Inquiry.objects.create(sender=self.tutee.user, recipient=self.admin, message="First inquiry")
        Inquiry.objects.create(sender=self.tutee.user, recipient=self.admin, message="Second inquiry")

        Notification.objects.create(user=self.tutee.user, message="First notification")
        Notification.objects.create(user=self.tutee.user, message="Second notification")

        inquiries = Inquiry.objects.all()
        notifications = Notification.objects.all()

        self.assertEqual(inquiries[0].message, "Second inquiry")
        self.assertEqual(inquiries[1].message, "First inquiry")
        self.assertEqual(notifications[0].message, "Second notification")
        self.assertEqual(notifications[1].message, "First notification")

    def test_str_method_returns_correct_format(self):
        self.inquiry = Inquiry.objects.create(
            sender=self.tutee.user,
            recipient=self.admin,
            message="I need help with my booking."
        )
        
        expected_str = f"Inquiry from {self.inquiry.sender.username} to {self.inquiry.recipient.username} - {self.inquiry.status}"
        
        self.assertEqual(str(self.inquiry), expected_str)
