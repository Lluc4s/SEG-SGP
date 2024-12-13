"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Tutee, Request, Notification

class RequestViewTestCase(TestCase):
    """Tests of the Request view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.url = reverse('requests')
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

    def test_home_url(self):
        self.assertEqual(self.url,'/requests/')

    def test_get_requests_as_authenticated_user(self):
        self.client.login(username=self.user.username, password='Password123')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests.html')

    def test_get_requests_as_staff_user(self):
        self.client.logout()
        self.client.login(username=self.staff_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests.html')
        self.assertTrue(response.context['user'].is_staff)
        self.assertIn('requests', response.context)
    
    def test_filter_requests_by_status_pending(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'status': 'Pending'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending')
    
    def test_filter_requests_by_status_approved(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, {'status': 'Approved'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Approved')
        
    def test_approve_request(self):
        self.client.login(username=self.staff_user.username, password='Password123')
        response = self.client.post(self.url, {'approve_request_id': self.request.id})
        self.assertEqual(response.status_code, 200)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'Approved')
        self.assertContains(response, "Request approved successfully.")
    
    def test_delete_request(self):
        self.client.login(username=self.staff_user.username, password='Password123')
        response = self.client.post(self.url, {'delete_request_id': self.request.id})
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(Request.DoesNotExist):
            self.request.refresh_from_db()
        self.assertContains(response, "Request deleted successfully.")
    
    def test_invalid_request_id(self):
        self.client.login(username=self.staff_user.username, password='Password123')
        response = self.client.post(self.url, {'approve_request_id': 9999})  
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Request not found.")
    
    def test_filter_requests_by_is_late(self):
        self.client.login(username=self.user.username, password='Password123')

        late_request = Request.objects.create(tutee=self.tutee, status="Pending", is_late=True, request_type="Change")
        on_time_request = Request.objects.create(tutee=self.tutee, status="Pending", is_late=False, request_type="Change")

        response = self.client.get(self.url, {'is_late': 'Late'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Late')
        self.assertNotContains(response, 'On Time')

        response = self.client.get(self.url, {'is_late': 'On Time'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'On Time')
        self.assertNotContains(response, 'Late')
    
    def test_get_requests_as_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/?next=/requests/')
    
    def test_notification_on_approve_request(self):
        self.client.login(username=self.staff_user.username, password='Password123')
        response = self.client.post(self.url, {'approve_request_id': self.request.id})
        self.assertEqual(response.status_code, 200)
        notification = Notification.objects.last()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.request.tutee.user)
        self.assertIn("approved", notification.message)

    def test_notification_on_delete_request(self):
        self.client.login(username=self.staff_user.username, password='Password123')
        response = self.client.post(self.url, {'delete_request_id': self.request.id})
        self.assertEqual(response.status_code, 200)
        notification = Notification.objects.last()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.request.tutee.user)
        self.assertIn("deleted", notification.message)
