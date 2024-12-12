from django.test import TestCase
from django.utils import timezone
from tutorials.forms import RequestForm
from tutorials.models import User, Booking, Tutor, Tutee, Request
from datetime import timedelta

class RequestFormTestCase(TestCase):
    """Unit tests for the RequestForm."""

    def setUp(self):
        self.tutor_user = User.objects.create(
            username="@janedoe",
            first_name="Jane",
            last_name="Doe",
            email="janedoe@example.com",
            is_tutor=True
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user, languages_specialised="Python, Java")

        self.tutee_user = User.objects.create(
            username="@charlie",
            first_name="Charlie",
            last_name="Doe",
            email="charliedoe@example.com",
            is_tutor=False
        )
        self.tutee = Tutee.objects.create(user=self.tutee_user)

        self.booking = Booking.objects.create(
            date_time=timezone.now(),
            duration=timedelta(minutes=30),
            language="Python",
            tutor=self.tutor,
            tutee=self.tutee,
            is_completed=False,
            is_paid=False,
            price=30.00
        )

        self.valid_new_booking_form = {
            'booking': None,
            'request_type': "New Booking",
            'frequency': "One-time",
            'details': "I need a new session for Python.",
            'language': "Python"
        }

        self.valid_change_booking_form = {
            'booking': self.booking.pk,
            'request_type': "Change",
            'frequency': "One-time",
            'details': "I need to reschedule this booking.",
            'language': "N/A"
        }

    def test_form_fields(self):
        """Test that the form has the required fields."""
        form = RequestForm(tutee=self.tutee)
        self.assertIn('booking', form.fields)
        self.assertIn('request_type', form.fields)
        self.assertIn('frequency', form.fields)
        self.assertIn('details', form.fields)
        self.assertIn('language', form.fields)

    def test_new_booking_form_is_valid(self):
        form = RequestForm(tutee=self.tutee, data=self.valid_new_booking_form)
        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")

    def test_change_booking_form_is_valid(self):
        form = RequestForm(tutee=self.tutee, data=self.valid_change_booking_form)
        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")

    def test_new_booking_form_is_invalid_for_change_request_type(self):
        invalid_data = self.valid_new_booking_form.copy()
        invalid_data['request_type'] = "Change" 
        form = RequestForm(tutee=self.tutee, data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_change_booking_form_is_invalid_for_language_provided(self):
        invalid_data = self.valid_change_booking_form.copy()
        invalid_data['language'] = "Python" 
        form = RequestForm(tutee=self.tutee, data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_change_booking_form_is_invalid_for_new_booking_request(self):
        invalid_data = self.valid_change_booking_form.copy()
        invalid_data['request_type'] = "New Booking"  
        form = RequestForm(tutee=self.tutee, data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_no_request(self):
        invalid_data = self.valid_change_booking_form.copy()
        invalid_data['request_type'] = ""  
        form = RequestForm(tutee=self.tutee, data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_no_frequency(self):
        invalid_data = self.valid_change_booking_form.copy()
        invalid_data['frequency'] = ""  
        form = RequestForm(tutee=self.tutee, data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_no_language(self):
        invalid_data = self.valid_change_booking_form.copy()
        invalid_data['language'] = ""  
        form = RequestForm(tutee=self.tutee, data=invalid_data)
        self.assertFalse(form.is_valid())
