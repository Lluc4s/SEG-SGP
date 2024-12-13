from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tutorials.models import Booking, Tutor, Tutee
from datetime import timedelta
from django.utils.timezone import now

User = get_user_model()

class EditBookingViewTest(TestCase):
    def setUp(self):
        # Create a test user (staff, tutor, and tutee) with unique email addresses
        self.staff_user = User.objects.create_user(username='staff_user', email='staff@example.com', password='password', is_staff=True)
        self.tutor_user = User.objects.create_user(username='tutor_user', email='tutor@example.com', password='password', is_tutor=True)
        self.tutee_user = User.objects.create_user(username='tutee_user', email='tutee@example.com', password='password')

        # Create related tutor and tutee profiles
        self.tutor = Tutor.objects.create(user=self.tutor_user, languages_specialised='Python, Java')
        self.tutee = Tutee.objects.create(user=self.tutee_user)

        # Create a test booking
        self.booking = Booking.objects.create(
            date_time=now() + timedelta(days=1),
            duration=timedelta(hours=1),
            language="Python",
            tutor=self.tutor,
            tutee=self.tutee,
            price=50.00,
        )

        # URLs
        self.edit_booking_url = reverse('edit_booking', kwargs={'booking_id': self.booking.id})
        self.redirect_url = reverse('dashboard')  # Replace with settings.REDIRECT_URL_WHEN_LOGGED_IN if needed


    def test_edit_booking_view_accessible_to_staff(self):
        self.client.login(username='staff_user', password='password')
        response = self.client.get(self.edit_booking_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_booking.html')

    def test_edit_booking_view_accessible_to_tutor(self):
        self.client.login(username='tutor_user', password='password')
        response = self.client.get(self.edit_booking_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_booking.html')

    def test_edit_booking_view_permission_denied_to_tutee(self):
        self.client.login(username='tutee_user', password='password')
        response = self.client.get(self.edit_booking_url)
        self.assertEqual(response.status_code, 403)


    def test_edit_booking_view_post_valid_data(self):
        self.client.login(username='tutor_user', password='password')
        valid_data = {
            'date_time': (now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S'),
            'duration': timedelta(minutes=30),
            'language': 'Python',
            'price': 100.00,
            'tutor': self.tutor.id,
            'tutee': self.tutee.id,
        }
        response = self.client.post(self.edit_booking_url, data=valid_data)
        if response.status_code == 200:
            print("Form errors:", response.context['form'].errors)  # Debugging step
        self.assertRedirects(response, self.redirect_url)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.price, 100.00)


    def test_edit_booking_view_post_invalid_data(self):
        self.client.login(username='tutor_user', password='password')
        invalid_data = {
            'date_time': '',  # Invalid: Missing required field
            'duration': '00:30:00',
            'language': 'Python',
            'price': 50.00,
        }
        response = self.client.post(self.edit_booking_url, data=invalid_data)
        form = response.context['form']  # Extract the form from the response context
        self.assertIn('This field is required.', form.errors['date_time'])


    def test_edit_booking_view_get_object(self):
        self.client.login(username='staff_user', password='password')
        response = self.client.get(self.edit_booking_url)
        self.assertEqual(response.context['object'], self.booking)

    def test_edit_booking_view_not_found(self):
        self.client.login(username='staff_user', password='password')
        invalid_url = reverse('edit_booking', kwargs={'booking_id': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)
