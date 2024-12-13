from django.test import TestCase
from tutorials.models import User,Request, NewBookingRequest, Tutee
from datetime import timedelta

class NewBookingRequestModelTestCase(TestCase):
    def setUp(self):
        self.tutee = Tutee.objects.create(
            user=User.objects.create_user(username="tutee1", password="password"),
        )
        self.request = Request.objects.create(
            tutee=self.tutee,
            request_type="New Booking"
        )
        self.new_booking_request = NewBookingRequest.objects.create(
            request=self.request,
            duration=timedelta(hours=1),
            language="English",
        )

    def test_new_booking_request_creation(self):
        self.assertEqual(self.new_booking_request.request, self.request)
        self.assertEqual(self.new_booking_request.frequency, "One-time")
        self.assertEqual(self.new_booking_request.duration, timedelta(hours=1))
        self.assertEqual(self.new_booking_request.language, "English")
        self.assertEqual(self.new_booking_request.details,"")

    def test_default_frequency(self):
        self.assertEqual(self.new_booking_request.frequency, "One-time")
