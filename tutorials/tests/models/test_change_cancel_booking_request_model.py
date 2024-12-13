from datetime import datetime, timedelta
from django.utils import timezone
from django.test import TestCase
from tutorials.models import User,Tutor,Request, ChangeCancelBookingRequest, Booking, Tutee  

class ChangeCancelBookingRequestModelTestCase(TestCase):
    def setUp(self):
        self.tutee = Tutee.objects.create(
            
            user=User.objects.create_user(username="tutee1", password="password123",email="tutee1@example.com"),
        )
        self.tutor = Tutor.objects.create(
            user=User.objects.create_user(username="tutor_username", password="password123",email="tutor_username@example.com"),
        )
        self.request = Request.objects.create(
            tutee=self.tutee,
            request_type="Change/Cancel"
        )
        self.booking = Booking.objects.create(
            date_time=timezone.make_aware(datetime(2023, 12, 1, 14, 0)),
            duration=timedelta(hours=2),
            language="Python",
            tutor=self.tutor,
            tutee=self.tutee,
            price=50.00
        )

        self.change_cancel_request = ChangeCancelBookingRequest.objects.create(
            request=self.request,
            booking=self.booking,
        )

    def test_change_cancel_request_creation(self):
        self.assertEqual(self.change_cancel_request.request, self.request)
        self.assertEqual(self.change_cancel_request.change_or_cancel, "Cancel")
        self.assertEqual(self.change_cancel_request.booking, self.booking)
    
    def test_details_can_be_black(self):
        self.assertEqual(self.change_cancel_request.details,"")
    
    def test_default_change_or_cancel(self):
        self.assertEqual(self.change_cancel_request.change_or_cancel, "Cancel")
