from django.test import TestCase
from django.utils.timezone import now, timedelta
from django.contrib.auth import get_user_model
from tutorials.models import Request,User, Tutee
from datetime import timedelta,date
from django.utils import timezone
from django.core.exceptions import ValidationError

class RequestModelTestCase(TestCase):

    def setUp(self):
        self.tutee_user = User.objects.create_user(
            username='@charlie', email='charliedoe@example.com', first_name='Charlie', last_name='Doe', is_tutor=False
        )
        self.tutee = Tutee.objects.create(user=self.tutee_user)

        self.request = Request.objects.create(
            tutee=self.tutee,
            request_type = "Change/Cancel Booking"
        )

    def create_user(self, username):
        return get_user_model().objects.create_user(username=username, password="password123")

    def test_request_fields_default_values(self):
        now = timezone.now()  
        self.assertEqual(self.request.is_late, False)
        self.assertEqual(self.request.status, "Pending")
    
        self.assertAlmostEqual(
            self.request.created_at.timestamp(),
            now.timestamp(),
            delta=1, 
        )

    def test_str_method_returns_correct_format(self):
        expected_str = f"{self.tutee.user.full_name()} - {self.request.request_type} - {self.request.status}"
        self.assertEqual(str(self.request), expected_str)

    def test_request_ordering(self):
        request2 = Request.objects.create(
            tutee=self.tutee,
            request_type="New Booking",
            created_at= now() - timedelta(days=2),
        )
        requests = Request.objects.all()
        self.assertEqual(requests.first(), self.request)
        self.assertEqual(requests.last(), request2)

    def test_get_term_start_date(self):
        self.request.created_at = date(2024, 11, 15)
        term_start_date = self.request.get_term_start_date()
        self.assertEqual(term_start_date, date(2024, 9, 1))

        self.request.created_at  = date(2024, 2, 1)
        term_start_date = self.request.get_term_start_date()
        self.assertEqual(term_start_date, date(2024, 1, 1))

        self.request.created_at  = date(2024, 6, 10)
        term_start_date = self.request.get_term_start_date()
        self.assertEqual(term_start_date, date(2024, 5, 1))

        self.request.created_at  = date(2024, 8, 15)
        term_start_date = self.request.get_term_start_date()
        self.assertIsNone(term_start_date)

    def test_request_status_choices(self):
        self.request.status = "Invalid"
        with self.assertRaises(ValidationError):
            self.request.full_clean()
            
    def test_is_late_must_be_boolean(self):
        self.request.is_late = "Not boolean"
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_request_type_choices(self):
        self.request.request_type = "Invalid"
        with self.assertRaises(ValidationError):
            self.request.full_clean()
