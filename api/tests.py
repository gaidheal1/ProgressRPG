from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class MeViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123"
        )
        self.url = reverse("me")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_me_view_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_me_view_unauthenticated(self):
        self.client.force_authenticate(user=None)  # remove authentication
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
