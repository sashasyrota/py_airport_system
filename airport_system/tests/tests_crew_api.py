from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport_system.models import Crew
from airport_system.serializers import CrewSerializer
from user.models import User

CREW_URL = reverse("airport_system:crew-list")


def crew_detail_url(crew_id: int):
    return reverse("airport_system:crew-detail", args=(crew_id,))


def sample_crew(**params):
    defaults = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


class UnauthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(CREW_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test", password="testtest")
        self.client.force_authenticate(self.user)
        self.crew1 = sample_crew()

    def test_crew_list(self):
        result = self.client.get(CREW_URL)
        crews = Crew.objects.all()
        serializer = CrewSerializer(crews, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data["results"], serializer.data)

    def test_retrieve_crew(self):
        url = crew_detail_url(self.crew1.id)
        result = self.client.get(url)
        serializer = CrewSerializer(self.crew1)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_airplane(self):
        result = self.client.post(CREW_URL)
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
        self.airplane = sample_crew()

    def test_admin_create_crew(self):
        data_crew = {
            "first_name": "test_first_name",
            "last_name": "test_last_name",
        }
        result = self.client.post(CREW_URL, data_crew)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
