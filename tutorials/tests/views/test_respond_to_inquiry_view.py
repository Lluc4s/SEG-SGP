from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from django.conf import settings

class TuteeSignUpViewTestCase(TestCase):
    """Test case for TuteeSignUpView."""

    def setUp(self):
        """Create test data."""
        self.url = reverse('tutee_sign_up')  # The URL for the TuteeSignUpView
        self.user_data = {
            'username': 'newtutee',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'password': 'securepassword',
        }

    def test_tutee_sign_up_get(self):
        """Test the GET request for the tutee sign-up page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Ensure the correct template is used
        self.assertTemplateUsed(response, 'sign_up.html')

    @patch('django.contrib.auth.login')  # Mocking login
    def test_tutee_sign_up_post_success(self, mock_login):
        """Test successful tutee sign-up and login."""
        # Send POST request with valid data
        response = self.client.post(self.url, self.user_data)

        # Check that the user is redirected to the correct page
        self.assertRedirects(response, reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN))

        # Ensure the user is created and logged in
        user = get_user_model().objects.get(username=self.user_data['username'])
        self.assertTrue(user.is_authenticated)  # User should be logged in
        mock_login.assert_called_once()  # Check that login was called

    def test_redirect_when_logged_in(self):
        """Test redirection when a user is already logged in."""
        # Create and log in a user
        user = get_user_model().objects.create_user(
            username='existinguser',
            first_name='Existing',
            last_name='User',
            email='existinguser@example.com',
            password='password123'
        )
        self.client.login(username='existinguser', password='password123')

        # Attempt to visit the tutee sign-up page
        response = self.client.get(self.url)

        # Check if the user is redirected to the correct URL
        self.assertRedirects(response, reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN))

    def test_invalid_tutee_sign_up_post(self):
        """Test failed tutee sign-up due to invalid data."""
        invalid_user_data = {
            'username': '',  # Invalid data (empty username)
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@example.com',
            'password': 'password123',
        }
        response = self.client.post(self.url, invalid_user_data)

        # Check if the form is invalid and the user is not created
        self.assertFormError(response, 'form', 'username', 'This field is required.')
        self.assertEqual(get_user_model().objects.count(), 0)  # No user should be created

    def test_tutee_sign_up_form_error(self):
        """Test that a user cannot sign up with an existing email."""
        existing_user = get_user_model().objects.create_user(
            username='existingtutee',
            first_name='Alice',
            last_name='Smith',
            email='existing@example.com',
            password='password123'
        )
        self.user_data['email'] = 'existing@example.com'  # Use an already existing email

        response = self.client.post(self.url, self.user_data)

        # Check if the form has an error for the email field
        self.assertFormError(response, 'form', 'email', 'Email address must be unique.')
        self.assertEqual(get_user_model().objects.count(), 1)  # Only the existing user should be present
