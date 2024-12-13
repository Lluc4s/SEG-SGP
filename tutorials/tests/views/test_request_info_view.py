from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Tutee, Request, NewBookingRequest, ChangeCancelBookingRequest

class RequestInfoViewTestCase(TestCase):
    """Tests of the RequestInfo view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('request_info', args=[1]) 
        self.user = User.objects.get(username='@johndoe')
        self.user.set_password('Password123')
        self.user.save()

        self.tutee = Tutee.objects.create(user=self.user)
        self.request = Request.objects.create(
            tutee=self.tutee,
            status="Pending",
            is_late=False,
            request_type="Change",
        )

        self.staff_user = User.objects.get(username="@janedoe")
        self.staff_user.set_password('Password123')
        self.staff_user.is_staff = True
        self.staff_user.save()

    def test_get_request_info_as_authenticated_user(self):
        self.client.login(username=self.user.username, password='Password123')

        response = self.client.get(reverse('request_info', args=[self.request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_info.html')
        self.assertEqual(response.context['request'], self.request)

    def test_get_request_info_as_unauthenticated_user(self):
        response = self.client.get(reverse('request_info', args=[self.request.id]))
        self.assertRedirects(response, '/?next=/requests/1')

    def test_get_request_info_without_related_requests(self):
        self.client.login(username=self.user.username, password='Password123')

        response = self.client.get(reverse('request_info', args=[self.request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['new_booking_request'])
        self.assertIsNone(response.context['change_cancel_request'])

    def test_get_request_info_with_invalid_request_id(self):
        self.client.login(username=self.user.username, password='Password123')

        response = self.client.get(reverse('request_info', args=[9999]))  
        self.assertEqual(response.status_code, 404) 
    
    def test_get_request_info_as_staff_user(self):
        self.client.login(username=self.staff_user.username, password='Password123')

        response = self.client.get(reverse('request_info', args=[self.request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_info.html')
        self.assertEqual(response.context['request'], self.request)

    def test_get_request_info_with_no_related_requests(self):
        """Test that the view correctly handles the absence of related requests."""
        self.client.login(username=self.user.username, password='Password123')

        response = self.client.get(reverse('request_info', args=[self.request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context.get('new_booking_request'))
        self.assertIsNone(response.context.get('change_cancel_request'))