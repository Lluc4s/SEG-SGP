from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.utils import timezone
from tutorials.models import Booking, Notification, Tutor, Tutee
from tutorials.forms import BookingForm

User = get_user_model()

class NewBookingViewTest(TestCase):

    def setUp(self):
        self.tutor_user = User.objects.create_user(
            username='tutor_user',
            email='tutor@example.com',
            password='password123',
            first_name='Tutor',
            last_name='User'
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user, languages_specialised="Python, Java")

        self.tutee_user = User.objects.create_user(
            username='tutee_user',
            email='tutee@example.com',
            password='password123',
            first_name='Tutee',
            last_name='User'
        )
        self.tutee = Tutee.objects.create(user=self.tutee_user)

        self.client.login(username='tutee_user', password='password123')
        self.new_booking_url = reverse('new_booking')  # Replace with your actual URL name

    def test_new_booking_view_get(self):
        response = self.client.get(self.new_booking_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_booking.html')
        self.assertIsInstance(response.context['form'], BookingForm)

    def test_new_booking_view_post_valid_data(self):
        data = {
            'date_time': timezone.now() + timezone.timedelta(days=1),
            'duration': '1:00:00',
            'language': 'Python',
            'tutor': self.tutor.id,
            'tutee': self.tutee.id,
            'price': '50.00',
        }

        response = self.client.post(self.new_booking_url, data, follow=True)
        self.assertRedirects(response, reverse('dashboard'))

        booking = Booking.objects.get(tutor=self.tutor, tutee=self.tutee)
        self.assertEqual(booking.language, 'Python')
        self.assertEqual(booking.price, 50.00)

        tutor_notification = Notification.objects.get(user=self.tutor_user)
        tutee_notification = Notification.objects.get(user=self.tutee_user)

        self.assertEqual(tutor_notification.message, "You have a new booking with Tutee User.")
        self.assertEqual(tutee_notification.message, "You have a new booking with Tutor User.")

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Booking successfully created!")

    def test_new_booking_view_post_invalid_data(self):
        data = {
            'date_time': '',
            'duration': '',
            'language': '',
            'tutor': self.tutor.id,
            'tutee': self.tutee.id,
            'price': '-10.00',
        }

        response = self.client.post(self.new_booking_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_booking.html')
        self.assertContains(response, "The price must be a positive number greater than zero.")
        self.assertEqual(Booking.objects.count(), 0)

    def test_new_booking_view_permission_denied(self):
        self.client.logout()
        response = self.client.get(self.new_booking_url)
        self.assertRedirects(response, f"/?next={self.new_booking_url}")
