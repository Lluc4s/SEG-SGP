"""Unit tests for the Tutor model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from tutorials.models import Tutor


class TutorModelTestCase(TestCase):
    """Unit tests for the Tutor model."""

    def test_valid_tutor(self):
        self._assert_tutor_is_valid()

    def test_user_must_not_be_blank(self):
        self.tutor.user = None
        self._assert_tutor_is_invalid()

    def test_languages_specialised_cannot_be_blank(self):
        self.tutor.languages_specialised = ""
        self._assert_tutor_is_invalid()

    def test_languages_specialised_can_contain_multiple_languages(self):
        languages = self.tutor.get_languages_list()
        self.assertTrue(len(languages) > 2) 
        self._assert_tutor_is_valid() 


    def test_languages_specialised_can_contain_one_language(self):
        self.tutor.languages_specialised = "Python"
        self._assert_tutor_is_valid()

    def test_get_languages_list_returns_correct_list(self):
        self.tutor.languages_specialised = "Python, Java, SQL"
        languages = self.tutor.get_languages_list()
        self.assertEqual(languages, ["Python", "Java", "SQL"])
