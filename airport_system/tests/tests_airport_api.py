from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport_system.models import Airport
from airport_system.serializers import (
    AirportSerializer
)
from user.models import User


AIRPORT_URL = reverse("airport_system:airport-list")


def sample_airport(**params):
    defaults = {
        "name": "test_airport",
        "closest_big_city": "test_city"
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def airplane_detail_url(airplane_id: int):
    return reverse("airport_system:airplane-detail", args=(airplane_id,))


def airport_detail_url(airport_id: int):
    return reverse("airport_system:airport-detail", args=(airport_id,))


class UnauthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(AIRPORT_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test", password="testtest")
        self.client.force_authenticate(self.user)
        self.airport1 = sample_airport()

    def test_airport_list(self):
        result = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data["results"], serializer.data)

    def test_retrieve_airport(self):
        url = airport_detail_url(self.airport1.id)
        result = self.client.get(url)
        serializer = AirportSerializer(self.airport1)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_airport(self):
        result = self.client.post(AIRPORT_URL)
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

    def test_admin_create_airport(self):
        data_airport = {
            "name": "test_airport"
        }
        result = self.client.post(AIRPORT_URL, data_airport)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
