from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from ..models import StatusUpdate
from rest_framework import status

User = get_user_model()

class TestCreateStatusUpdateAPI(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email="test@test.com", is_teacher=False)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.status_update_url = '/api/create_status_update/'  # Update with your actual URL

    def test_create_status_update(self):
        response = self.client.post(self.status_update_url, {'status': 'This is a test status update.'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StatusUpdate.objects.count(), 1)
        self.assertEqual(StatusUpdate.objects.first().status, 'This is a test status update.')
        self.assertEqual(StatusUpdate.objects.first().user, self.user)

    def test_create_status_update_unauthorized(self):
        # Test without authentication
        self.client.logout()
        response = self.client.post(self.status_update_url, {'status': 'This is a test status update.'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Or the appropriate status code for unauthorized access
    
    def test_create_status_update_invalid_data(self):
        response = self.client.post(self.status_update_url, {'status': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)