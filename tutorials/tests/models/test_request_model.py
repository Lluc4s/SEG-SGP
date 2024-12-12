from django.test import TestCase
from django.utils.timezone import now, timedelta
from django.contrib.auth import get_user_model
from tutorials.models import Request,Booking, Tutor,User, Tutee
from datetime import datetime, timedelta,date
from django.core.exceptions import ValidationError



class RequestModelTestCase(TestCase):

    def setUp(self):
        self.tutor_user = User.objects.create_user(
            username='@janedoe', email='janedoe@example.com', first_name='Jane', last_name='Doe', is_tutor=True
        )
        self.tutee_user = User.objects.create_user(
            username='@charlie', email='charliedoe@example.com', first_name='Charlie', last_name='Doe', is_tutor=False
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)
        self.tutee = Tutee.objects.create(user=self.tutee_user)
        self.booking = Booking.objects.create(
            date_time=datetime(2023, 12, 1, 14, 0),
            duration=timedelta(hours=2),
            language="Python",
            tutor=self.tutor,
            tutee=self.tutee,
            price=50.00
        )

        self.request = Request.objects.create(
            tutee=self.tutee,
            booking=self.booking,
            details="Please reschedule to next week.",
        )

    def create_user(self, username):
        return get_user_model().objects.create_user(username=username, password="password123")

    def test_request_fields_default_values(self):

        self.assertEqual(self.request.request_type, "Change Booking")
        self.assertEqual(self.request.frequency, "One-time")
        self.assertEqual(self.request.status, "Pending")

    def test_str_method_returns_correct_format(self):
        expected_str = f"{self.tutee.user.full_name()} - Change Booking - Pending"
        self.assertEqual(str(self.request), expected_str)

    def test_request_timeliness_delayed(self):
        term_start_date = date(self.booking.date_time.year, 9, 1) 
        self.request.created_at = term_start_date + timedelta(days=25)
        self.request.save()
        self.assertEqual(self.request.timeliness, "Delayed")

    def test_request_timeliness_on_time(self):
        term_start_date = date(self.booking.date_time.year, 9, 1) 
        self.request.created_at = term_start_date - timedelta(weeks=5)
        self.request.save()
        self.assertEqual(self.request.timeliness, "On Time")

    def test_request_ordering(self):
        earlier_request = Request.objects.create(
            tutee=self.tutee,
            booking=self.booking,
            request_type="Cancel",
            frequency="One-time",
            created_at=now() - timedelta(days=2),
        )
        requests = Request.objects.all()
        self.assertEqual(requests.first(), self.request)
        self.assertEqual(requests.last(), earlier_request)

    def test_request_get_term_and_start_date(self):
        term_start_date = self.request.get_term_and_start_date(self.booking.date_time.date())
        self.assertEqual(term_start_date, date(self.booking.date_time.year, 9, 1))

    def test_request_status_choices(self):
        self.request.status = "Invalid"
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_request_type_choices(self):
        self.request.request_type = "Invalid"
        with self.assertRaises(ValidationError):
            self.request.full_clean()

