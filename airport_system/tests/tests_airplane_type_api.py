from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport_system.models import AirplaneType
from airport_system.serializers import AirplaneTypeSerializer
from user.models import User

AIRPLANE_TYPE_URL = reverse("airport_system:airplanetype-list")


def airplane_type_detail_url(airplane_type_id: int):
    return reverse(
        "airport_system:airplanetype-detail",
        args=(airplane_type_id,)
    )


def sample_airplane_type(**params):
    defaults = {
        "name": "test_name"
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


class UnauthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test", password="testtest")
        self.client.force_authenticate(self.user)
        self.airplane_type1 = sample_airplane_type()

    def test_airplane_type_list(self):
        result = self.client.get(AIRPLANE_TYPE_URL)
        airplane_types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_types, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data["results"], serializer.data)

    def test_retrieve_airplane_type(self):
        url = airplane_type_detail_url(self.airplane_type1.id)
        result = self.client.get(url)
        serializer = AirplaneTypeSerializer(self.airplane_type1)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_airplane(self):
        result = self.client.post(AIRPLANE_TYPE_URL)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


class AdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            email="admin_test",
            password="admin_testtest",
            is_staff=True
        )
        self.client.force_authenticate(self.admin_user)
        self.airplane_type = sample_airplane_type()

    def test_admin_create_airplane_type(self):
        data_airplane_type = {
            "name": "test_name"
        }
        result = self.client.post(AIRPLANE_TYPE_URL, data_airplane_type)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
