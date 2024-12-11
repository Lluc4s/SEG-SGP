from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from tutorials.models import Booking, Tutor, Tutee, User

class BookingModelTestCase(TestCase):

    def setUp(self):
        self.tutor_user = User.objects.create_user(
            username='@janedoe', email='janedoe@example.com', first_name='Jane', last_name='Doe', is_tutor=True
        )

        self.tutee_user = User.objects.create_user(
            username='@charliedoe', email='charliedoe@example.com', first_name='Charlie', last_name='Doe', is_tutor=False
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

    def test_tutor_languages_specialised_includes_booking_languages(self):
        self.tutor.languages_specialised = "Python, Java"
        self.booking.language = "Python"
        self.booking.save()
        self.assertIn(self.booking.language,self.tutor.languages_specialised)

    def test_tutor_languages_sepcialised_does_not_include_booking_language_is_invalid(self):
        self.tutor.languages_specialised = "Python, Java"
        self.booking.language = "SQL"
        self.assertNotIn(self.booking.language,self.tutor.languages_specialised)
    
    def test_str_method_returns_correct_format(self):
        expected_str = "12/01/2023 02:00 PM - 04:00 PM : Python with Jane Doe"
        self.assertEqual(str(self.booking), expected_str)
    
    def test_meta_ordering(self):
        earlier_booking = Booking.objects.create(
            date_time=datetime(2023, 11, 30, 10, 0),
            duration=timedelta(hours=1),
            language="Python",
            tutor=self.tutor,
            tutee=self.tutee,
            price=50.00
        )
        bookings = Booking.objects.all()
        self.assertEqual(bookings[0], earlier_booking)

    def test_blank_date_time_is_invalid(self):
        self.booking.date_time = None
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def test_duration_must_be_valid(self):
        self.booking.duration = timedelta(hours=-1)
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def test_language_must_be_valid_choice(self):
        self.booking.language = "InvalidLanguage"
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def test_is_completed_default_value(self):
        self.assertFalse(self.booking.is_completed)

    def test_price_cannot_be_negative(self):
        self.booking.price = -10.00
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

    def test_price_can_be_zero(self):
        self.booking.price = 0.00
        self.booking.full_clean() 
    def test_is_completed_must_be_boolean(self):
        with self.assertRaises(ValidationError, msg="is_completed must be a boolean value"):
            self.booking.is_completed = "not_boolean"
            self.booking.full_clean()

    def test_is_paid_must_be_boolean(self):
        with self.assertRaises(ValidationError, msg="is_completed must be a boolean value"):
            self.booking.is_paid = "not_boolean"
            self.booking.full_clean()



