from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User, Tutor
from django.db.utils import IntegrityError


class TutorModelTestCase(TestCase):
    """Unit tests for the Tutor model."""
    def setUp(self):
        user = User("@janedoe","jane","doe","janedoe@example.com",True)
        languages = "Python, Java"
        self.tutor = Tutor(user = user, languages_specialised = languages)
    
    def _assert_tutor_is_valid(self):
        try:
            self.tutor.full_clean()
        except ValidationError:
            self.fail("Tutor instance should be valid")
    
    def test_blank_user_is_invalid(self):
        self.tutor.user = User("@","","","@example.com",True)
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    def test_languages_specialised_cannot_be_blank(self):
        self.tutor.languages_specialised = ""
        with self.assertRaises(ValidationError):
            self.tutor.full_clean()

    def test_languages_specialised_can_contain_multiple_languages(self):
        self.tutor.languages_specialised = "Python, Java, SQL"
        languages = self.tutor.get_languages_list()
        self.assertTrue(len(languages) > 2) 

    def test_languages_specialised_can_contain_one_language(self):
        self.tutor.languages_specialised = "Python"
        languages = self.tutor.get_languages_list()
        self.assertEqual(len(languages),1) 

    def test_get_languages_list_returns_correct_list(self):
        self.tutor.languages_specialised = "Python, Java, SQL"
        languages = self.tutor.get_languages_list()
        self.assertEqual(languages, ["Python", "Java", "SQL"])
    
    def tutor_user_must_be_unique(self):
        self.tutor.save()
        user = User("@janedoe","jane","doe","janedoe@example.com",True)
        languages = "Java, SQL"
        with self.assertRaises(IntegrityError):
            Tutor.objects.create(user = user, languages_specialised = languages)
