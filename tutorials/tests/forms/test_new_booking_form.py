from django.test import TestCase
from django.utils import timezone
from tutorials.forms import BookingForm
from tutorials.models import Booking, Tutor, Tutee, User
from datetime import timedelta

class NewBookingFormTestCase(TestCase):
    """Unit tests for the NewBookingForm."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.tutor_user = User.objects.get(username="@johndoe")
        self.tutor_user.is_tutor = True
        self.tutor = Tutor.objects.create(user=self.tutor_user, languages_specialised="Python, Java")
        
        self.tutee_user = User.objects.get(username="@janedoe")
        self.tutee = Tutee.objects.create(user=self.tutee_user)
        
        self.valid_form_data = {
            'date_time': timezone.now().replace(second=0, microsecond=0) + timedelta(minutes=1),
            'duration': timedelta(minutes=30),
            'language': "Python",
            'tutor': self.tutor,
            'tutee': self.tutee,
            'price': 30.00
        }

    def test_form_fields(self):
        """Test if all expected fields are present in the form."""
        form = BookingForm()
        self.assertIn('date_time', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('language', form.fields)
        self.assertIn('tutor', form.fields)
        self.assertIn('tutee', form.fields)
        self.assertIn('price', form.fields)

    def test_form_is_valid(self):
        form = BookingForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")

    def test_form_is_invalid_for_no_price(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['price'] = 0
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_negative_price(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['price'] = -1
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_no_language(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['language'] = ""
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_when_language_not_in_tutor_languages(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['language'] = "C++"
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_when_no_duration(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['duration'] = None
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_when_negative_duration(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['duration'] = timedelta(minutes=-30)
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_when_invalid_duration(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['duration'] = timedelta(minutes=15)
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_when_bookings_overlap(self):
        Booking.objects.create(
            date_time=timezone.now().replace(second=0, microsecond=0) + timedelta(minutes=1),
            duration=timedelta(minutes=30),
            language="Python",
            tutor=self.tutor,
            tutee=self.tutee,
            price=30.00
        )

        overlapping_data = self.valid_form_data.copy()
        form = BookingForm(data=overlapping_data)
        self.assertFalse(form.is_valid())

    def test_valid_form_can_be_saved(self):
        form = BookingForm(data=self.valid_form_data)
        before_count = Booking.objects.count()
        form.save()
        after_count = Booking.objects.count()
        self.assertEqual(before_count + 1, after_count)

    def test_booking_is_created_with_correct_tutor_and_tutee(self):
        form = BookingForm(data=self.valid_form_data)
        form.save()
        booking = Booking.objects.latest('date_time')
        self.assertEqual(booking.tutor, self.tutor)
        self.assertEqual(booking.tutee, self.tutee)

    def test_min_date_time_is_set_correctly(self):
        form = BookingForm()
        now = timezone.now()
        rounded_now = now.replace(second=0, microsecond=0)
        if now.minute % 30 != 0:
            rounded_now += timedelta(minutes=(30 - now.minute % 30))
        
        self.assertEqual(form.fields['date_time'].widget.attrs['min'], rounded_now.strftime('%Y-%m-%dT%H:%M'))
        
    def test_step_attribute_for_date_time(self):
        form = BookingForm()
        self.assertEqual(form.fields['date_time'].widget.attrs['step'], '1800')
    
    def test_form_is_invalid_for_invalid_tutor(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['tutor'] = ""
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_invalid_tutee(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['tutee'] = ""
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_tutee_passed_as_tutor(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['tutor'] = self.tutee_user
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_invalid_tutor_passed_as_tutee(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['tutee'] = self.tutor_user
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_when_date_time_in_the_past(self):
        past_date_time = timezone.now() - timedelta(days=1) 
        invalid_data = self.valid_form_data.copy()
        invalid_data['date_time'] = past_date_time.replace(second=0, microsecond=0)
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_no_date_time(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['date_time'] = None
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_invalid_date_time(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['date_time'] = "Invalid Date Time"
        form = BookingForm(data=invalid_data)
        self.assertFalse(form.is_valid())