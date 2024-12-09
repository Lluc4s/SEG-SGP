from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User, Tutee
from django.db.utils import IntegrityError


class TuteeModelTestCase(TestCase):
    def setUp(self):
        user = User("@charlie","charlie","doe","clarliedoe@example.com",False)
        languages = "Python, Java"
        self.tutee = Tutee(user = user)
    
    def _assert_tutee_is_valid(self):
        try:
            self.tutee.full_clean()
        except ValidationError:
            self.fail("Tutee instance should be valid")
    
    def test_blank_user_is_invalid(self):
        self.tutee.user = User("@","","","@example.com",False)
        with self.assertRaises(ValidationError):
            self.tutee.full_clean()

    def tutee_user_must_be_unique(self):
        self.tutee.save()
        user = User("@charlie","charlie","doe","clarliedoe@example.com",False)
        with self.assertRaises(IntegrityError):
            Tutee.objects.create(user = user)

    def test_str_method_returns_username(self):
        self.assertEqual(str(self.tutee), self.user.username)
