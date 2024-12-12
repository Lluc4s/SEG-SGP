from django.test import TestCase
from tutorials.forms import NewBookingRequestForm
from tutorials.models import Tutee, User, NewBookingRequest
from datetime import timedelta


class NewBookingRequestFormTestCase(TestCase):
    """Unit tests for the NewBookingRequestForm."""

    fixtures = ['tutorials/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username="@johndoe")
        self.tutee = Tutee.objects.create(user=self.user)

        self.valid_form_data = {
            'frequency': "Weekly",
            'duration': timedelta(minutes=60),
            'language': "Python",
            'details': "I would like weekly Python sessions.",
        }

    def test_form_fields(self):
        """Test that the form has the required fields."""
        form = NewBookingRequestForm()
        self.assertIn('frequency', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('language', form.fields)
        self.assertIn('details', form.fields)

    def test_form_is_valid(self):
        form = NewBookingRequestForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")

    def test_form_is_invalid_for_no_frequency(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['frequency'] = ""
        form = NewBookingRequestForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_empty_language(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['language'] = ""
        form = NewBookingRequestForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_no_duration(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['duration'] = timedelta(minutes=0)
        form = NewBookingRequestForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_negative_duration(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['duration'] = timedelta(minutes=-30)
        form = NewBookingRequestForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_invalid_duration(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['duration'] = timedelta(minutes=15)
        form = NewBookingRequestForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_valid_form_can_be_saved(self):
        form = NewBookingRequestForm(data=self.valid_form_data)
        form.instance.tutee = self.tutee
        before_count = NewBookingRequest.objects.count()
        form.save()
        after_count = NewBookingRequest.objects.count()
        self.assertEqual(before_count + 1, after_count)

    def test_tutee_is_assigned_to_request(self):
        form = NewBookingRequestForm(data=self.valid_form_data)
        form.instance.tutee = self.tutee
        form.save()
        self.assertEqual(form.instance.request.tutee, self.tutee)
