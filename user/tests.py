from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

REGISTER_URL = reverse("user:create")


class UserTests(TestCase):

    def test_email_instead_username(self):
        client = APIClient()
        result = client.post(REGISTER_URL)
        self.assertNotIn("username", result.data)
