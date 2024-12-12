from django.test import TestCase
from tutorials.forms import InquiryForm
from tutorials.models import Tutee, User, Inquiry
from datetime import timedelta

class NewBookingRequestFormTestCase(TestCase):
    """Unit tests for the NewBookingRequestForm."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user_1 = User.objects.get(username="@johndoe")
        self.user_1.is_staff = True
        self.user_2 = User.objects.get(username="@janedoe")
        self.user_2.is_staff = False

        self.valid_form_data = {
            'message' : "I want to have a new tutor",
            'recipient' : self.user_1
        }

    def test_form_fields(self):
        """Test that the form has the required fields."""
        form = InquiryForm()
        self.assertIn('message', form.fields)
        self.assertIn('recipient', form.fields)

    def test_form_is_valid(self):
        form = InquiryForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

    def test_form_is_invalid_for_empty_message(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['message'] = ""
        form = InquiryForm(data=invalid_data)      
        self.assertFalse(form.is_valid())
    
    def test_form_is_valid_for_no_recipient_for_non_staff(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['recipient'] = ""
        form = InquiryForm(data=invalid_data, user=self.user_2)      
        self.assertTrue(form.is_valid())
    
    def test_form_is_invalid_for_invalid_recipient(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['recipient'] = 999
        form = InquiryForm(data=invalid_data, user=self.user_2) 
        self.assertFalse(form.is_valid())
    
    def test_form_can_be_saved_with_sender(self):
        form = InquiryForm(data=self.valid_form_data, user=self.user_1)
        before_count = Inquiry.objects.count()
        form.instance.sender = self.user_1
        form.save()
        after_count = Inquiry.objects.count()
        self.assertEqual(before_count+1, after_count)
    