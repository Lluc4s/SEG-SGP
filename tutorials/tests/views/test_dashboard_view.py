from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timezone
from tutorials.models import Booking, Tutor, Tutee
from datetime import timedelta
User = get_user_model()


class DashboardViewTest(TestCase):
    from datetime import timedelta

class DashboardViewTest(TestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin_user', email='admin@test.com', password='adminpass', is_staff=True
        )
        self.tutor_user = User.objects.create_user(
            username='tutor_user', email='tutor@test.com', password='tutorpass', is_tutor=True
        )
        self.tutee_user = User.objects.create_user(
            username='tutee_user', email='tutee@test.com', password='tuteepass'
        )

        # Create related models
        self.tutor = Tutor.objects.create(user=self.tutor_user)
        self.tutee = Tutee.objects.create(user=self.tutee_user)

        # Create two bookings with different completion statuses
        self.booking1 = Booking.objects.create(
            date_time=now() - timedelta(days=1),  # In the past
            duration=timedelta(hours=1),
            language="Python",
            tutor=self.tutor,
            tutee=self.tutee,
            is_completed=True,  # Marked as completed
        )
        self.booking2 = Booking.objects.create(
            date_time=now() + timedelta(days=1),  # In the future
            duration=timedelta(hours=1),
            language="Java",
            tutor=self.tutor,
            tutee=self.tutee,
            is_completed=False,  # Not completed
        )


    def test_dashboard_view_accessible_to_staff(self):
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('bookings', response.context)

    def test_dashboard_view_accessible_to_tutor(self):
        self.client.login(username='tutor_user', password='tutorpass')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('bookings', response.context)

    def test_dashboard_view_accessible_to_tutee(self):
        self.client.login(username='tutee_user', password='tuteepass')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('bookings', response.context)

    def test_dashboard_view_filter_by_status(self):
        # Login as staff user
        self.client.login(username='admin_user', password='adminpass')

        # Apply filter for completed bookings
        response = self.client.get(reverse('dashboard'), {'status': 'Completed'})
        bookings = response.context['bookings']

        # Assert only the completed booking is returned
        self.assertEqual(len(bookings), 1)  # Ensure only one booking is completed
        self.assertIn(self.booking1, bookings)
        self.assertNotIn(self.booking2, bookings)

    def test_dashboard_view_filter_by_tutor(self):
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.get(reverse('dashboard'), {'tutor': 'tutor_user'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['bookings']), 2)  # All bookings belong to this tutor

    def test_dashboard_view_filter_by_tutee(self):
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.get(reverse('dashboard'), {'tutee': 'tutee_user'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['bookings']), 2)  # All bookings belong to this tutee

    def test_dashboard_view_pagination(self):
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.get(reverse('dashboard'), {'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertIn('bookings', response.context)
        self.assertEqual(len(response.context['bookings']), 2)  # Only 2 bookings in total

    def test_dashboard_view_post_delete_booking(self):
        self.client.login(username='admin_user', password='adminpass')

        response = self.client.post(reverse('dashboard'), {'delete_booking_id': self.booking1.id})

        # Verify redirect after deleting
        self.assertRedirects(response, reverse('dashboard'))

        # Verify the booking is deleted
        with self.assertRaises(Booking.DoesNotExist):
            Booking.objects.get(id=self.booking1.id)

    def test_dashboard_view_invalid_delete_booking(self):
        self.client.login(username='admin_user', password='adminpass')
        response = self.client.post(reverse('dashboard'), {'delete_booking_id': 999})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Booking not found.")
