"""Unit tests of the tutor sign up form."""
from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from tutorials.forms import TutorSignUpForm
from tutorials.models import User, Tutor

class TutorSignUpFormTestCase(TestCase):
    """Unit tests of the sign up form."""

    def setUp(self):
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe',
            'email': 'janedoe@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
            'languages_specialised' : ["Python",  "Java"]
        }

    def test_valid_sign_up_form(self):
        form = TutorSignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = TutorSignUpForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('languages_specialised', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('new_password', form.fields)
        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        self.assertIn('password_confirmation', form.fields)
        password_confirmation_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))

    def test_form_uses_model_validation(self):
        self.form_input['username'] = 'badusername'
        form = TutorSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = TutorSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = TutorSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = TutorSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = TutorSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = TutorSignUpForm(data=self.form_input)
        before_count = Tutor.objects.count()
        form.save()
        after_count = Tutor.objects.count()
        self.assertEqual(after_count, before_count+1)

        tutor = Tutor.objects.get(user__username='@janedoe')
        user = tutor.user
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)

    def test_form_is_invalid_for_empty_first_name(self):
        invalid_data = self.form_input.copy()
        invalid_data['first_name'] = ""
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_invalid_first_name(self):
        invalid_data = self.form_input.copy()
        invalid_data['first_name'] = 9890
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_empty_last_name(self):
        invalid_data = self.form_input.copy()
        invalid_data['last_name'] = ""
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_invalid_last_name(self):
        invalid_data = self.form_input.copy()
        invalid_data['last_name'] = 9890
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_empty_email(self):
        invalid_data = self.form_input.copy()
        invalid_data['email'] = ""
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_invalid_email(self):
        invalid_data = self.form_input.copy()
        invalid_data['email'] = 9890
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_empty_username(self):
        invalid_data = self.form_input.copy()
        invalid_data['username'] = ""
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_invalid_username(self):
        invalid_data = self.form_input.copy()
        invalid_data['username'] = 9890
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_empty_languages_specialised(self):
        invalid_data = self.form_input.copy()
        invalid_data['languages_specialised'] = []
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_invalid_languages_specialised(self):
        invalid_data = self.form_input.copy()
        invalid_data['languages_specialised'] = 9890
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_unavailable_languages_specialised(self):
        invalid_data = self.form_input.copy()
        invalid_data['languages_specialised'] = ["English", "German"]
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_empty_password(self):
        invalid_data = self.form_input.copy()
        invalid_data['new_password'] = ""
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_username_not_starting_with_at(self):
        invalid_data = self.form_input.copy()
        invalid_data['username'] = "janedoe" 
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_duplicate_email(self):
        user = User.objects.create_user(
            username='@janedoe_different',
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.org',
            password='Password123'
        )
        Tutor.objects.create(user=user) 
        form = TutorSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_duplicate_username(self):
        user = User.objects.create_user(
            username='@janedoe',
            first_name='Jane',
            last_name='Doe',
            email='janedoe_different@example.org',
            password='Password123'
        )
        Tutor.objects.create(user=user) 
        form = TutorSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_when_passwords_do_not_match(self):
        invalid_data = self.form_input.copy()
        invalid_data['password_confirmation'] = "password123"
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password_confirmation', form.errors)
    
    def test_form_trims_leading_and_trailing_spaces(self):
        invalid_data = self.form_input.copy()
        invalid_data['first_name'] = "  Jane  "
        invalid_data['last_name'] = "  Doe  "
        invalid_data['username'] = "  @janedoe  "
        form = TutorSignUpForm(data=invalid_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.username, "@janedoe")
    
    def test_form_is_invalid_for_whitespace_only_first_name(self):
        invalid_data = self.form_input.copy()
        invalid_data['first_name'] = "   "
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_whitespace_only_last_name(self):
        invalid_data = self.form_input.copy()
        invalid_data['last_name'] = "   "
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_case_insensitive_duplicate_email(self):
        User.objects.create_user(
            username='@janedoe2',
            first_name='Jane',
            last_name='Doe',
            email='JANEDOE@example.org',
            password='Password123'
        )
        form = TutorSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_mixed_valid_and_invalid_languages_specialised(self):
        invalid_data = self.form_input.copy()
        invalid_data['languages_specialised'] = ["Python", "German"] 
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_form_is_invalid_for_more_than_maximum_languages_specialised(self):
        invalid_data = self.form_input.copy()
        invalid_data['languages_specialised'] = ["Python", "Java", "C++", "JavaScript", "R", "SQL", "Ruby"]
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_form_is_invalid_for_non_string_in_languages_specialised(self):
        invalid_data = self.form_input.copy()
        invalid_data['languages_specialised'] = ["Python", 123]
        form = TutorSignUpForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    