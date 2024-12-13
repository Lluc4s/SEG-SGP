from django.test import TestCase
from django.utils import timezone
from tutorials.forms import ChangeCancelBookingRequestForm
from tutorials.models import Booking, Tutee, User, Tutor, ChangeCancelBookingRequest
from datetime import timedelta

class ChangeCancelBookingRequestFormTestCase(TestCase):
    """Unit tests for the ChangeCancelBookingRequestForm."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.tutor_user = User.objects.get(username="@johndoe")
        self.tutor = Tutor.objects.create(user=self.tutor_user, languages_specialised="Python, Java")

        self.tutee_user = User.objects.get(username="@janedoe")
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
        self.valid_form_data = {
            'booking': self.booking.pk,
            'change_or_cancel': 'Cancel',
            'details': "I need to cancel my booking.",
        }

    def test_form_fields(self):
        form = ChangeCancelBookingRequestForm(tutee=self.tutee)
        self.assertIn('booking', form.fields)
        self.assertIn('change_or_cancel', form.fields)
        self.assertIn('details', form.fields)

    def test_form_is_valid(self):
        form = ChangeCancelBookingRequestForm(data=self.valid_form_data, tutee=self.tutee)
        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")

    def test_form_is_invalid_for_tutor_user(self):
        with self.assertRaises(ValueError):
            form = ChangeCancelBookingRequestForm(data=self.valid_form_data, tutee=self.tutor)
            form.is_valid()

    def test_form_is_invalid_when_no_change_cancel_field(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['change_or_cancel'] = ""
        form = ChangeCancelBookingRequestForm(data=invalid_data, tutee=self.tutee)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_invalid_change_cancel_field(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['change_or_cancel'] = "New"
        form = ChangeCancelBookingRequestForm(data=invalid_data, tutee=self.tutee)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_when_no_booking(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['booking'] = ""
        form = ChangeCancelBookingRequestForm(data=invalid_data, tutee=self.tutee)
        self.assertFalse(form.is_valid())

    def test_valid_form_can_be_saved(self):
        form = ChangeCancelBookingRequestForm(data=self.valid_form_data, tutee=self.tutee)
        form.instance.tutee = self.tutee
        before_count = ChangeCancelBookingRequest.objects.count()
        form.save()
        after_count = ChangeCancelBookingRequest.objects.count()
        self.assertEqual(before_count + 1, after_count)

    def test_tutee_is_assigned_to_request(self):
        form = ChangeCancelBookingRequestForm(data=self.valid_form_data, tutee=self.tutee)
        form.instance.tutee = self.tutee
        form.save()
        self.assertEqual(form.instance.request.tutee, self.tutee)
    
    def test_form_is_invalid_for_completed_booking(self):
        self.booking.is_completed = True
        self.booking.save()
        form = ChangeCancelBookingRequestForm(data=self.valid_form_data, tutee=self.tutee)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_other_tutee(self):
        other_tutee_user = User.objects.get(username="@petrapickles")
        other_tutee = Tutee.objects.create(user=other_tutee_user)
        invalid_data = self.valid_form_data.copy()
        invalid_data['booking'] = self.booking.pk
        form = ChangeCancelBookingRequestForm(data=invalid_data, tutee=other_tutee)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_completed_booking_on_change(self):
        self.booking.is_completed = True
        self.booking.save()
        invalid_data = self.valid_form_data.copy()
        invalid_data['change_or_cancel'] = "Change"
        form = ChangeCancelBookingRequestForm(data=invalid_data, tutee=self.tutee)
        self.assertFalse(form.is_valid())