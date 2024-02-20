from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from ..models import StatusUpdate
from ..serializers import StatusUpdateSerializer

User = get_user_model()

class TestStatusUpdateSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email="test@test.com", is_teacher=False)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.status_update_data = {'status': 'This is a test status update.'}
    
    def test_serializer_with_valid_data(self):
        serializer = StatusUpdateSerializer(data=self.status_update_data, context={'request': self.client.request})
        self.assertTrue(serializer.is_valid())
        status_update = serializer.save(user=self.user)
        self.assertEqual(StatusUpdate.objects.count(), 1)
        self.assertEqual(status_update.status, 'This is a test status update.')
        self.assertEqual(status_update.user, self.user)

    def test_serializer_with_invalid_data(self):
        self.status_update_data['status'] = ''
        serializer = StatusUpdateSerializer(data=self.status_update_data, context={'request': self.client.request})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, {'status': ['Status update cannot be empty.']})
        self.assertEqual(StatusUpdate.objects.count(), 0)