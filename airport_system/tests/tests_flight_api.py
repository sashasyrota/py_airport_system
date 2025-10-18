from datetime import datetime

from django.db.models import F, Count
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport_system.models import Flight
from airport_system.serializers import (
    FlightListSerializer,
    FlightRetrieveSerializer
)
from airport_system.tests.tests_airplane_api import sample_airplane
from airport_system.tests.tests_airport_api import sample_airport
from airport_system.tests.tests_route_api import sample_route
from user.models import User

FLIGHT_URL = reverse("airport_system:flight-list")


def sample_flight(**params):
    defaults = {
        "route": None,
        "airplane": None,
        "departure_time": datetime(2025, 2, 2, 12, 2),
        "arrival_time": datetime(2025, 2, 2, 14, 2)
    }
    defaults.update(params)
    return Flight.objects.create(**defaults)


def flight_detail_url(flight_id: int):
    return reverse("airport_system:flight-detail", args=(flight_id,))


class UnauthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(FLIGHT_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test", password="testtest")
        self.client.force_authenticate(self.user)
        self.airplane = sample_airplane()
        self.airport1 = sample_airport()
        self.airport2 = sample_airport(name="test_airport2")
        self.airport3 = sample_airport(name="test_airport3")
        self.route1 = sample_route(
            source=self.airport1,
            destination=self.airport2
        )
        self.route2 = sample_route(
            source=self.airport2,
            destination=self.airport1
        )
        self.route3 = sample_route(
            source=self.airport2,
            destination=self.airport3
        )
        self.flight1 = sample_flight(route=self.route1, airplane=self.airplane)
        sample_flight(route=self.route2, airplane=self.airplane)
        sample_flight(route=self.route3, airplane=self.airplane)

    def test_flight_list(self):
        result = self.client.get(FLIGHT_URL)
        flights = Flight.objects.all().annotate(
            num_available_seats=F("airplane__rows")
            * F("airplane__seats_in_row") - Count("ticket")
        )
        serializer = FlightListSerializer(flights, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data["results"], serializer.data)

    def test_filter_flight_by_source_destination(self):
        flights = Flight.objects.all()
        flights_with_params = flights.filter(
            route__source=self.airport2.id,
            route__destination=self.airport1.id).annotate(
            num_available_seats=F("airplane__rows")
            * F("airplane__seats_in_row") - Count("ticket")
        )
        result_with_params = self.client.get(
            f"{FLIGHT_URL}"
            f"?source_airport={self.airport2.id}"
            f"&destination_airport={self.airport1.id}"
        )
        serializer_with_params = (
            FlightListSerializer(flights_with_params, many=True)
        )
        flights_without_params = flights.annotate(
            num_available_seats=F("airplane__rows")
            * F("airplane__seats_in_row") - Count("ticket")
        )
        result_without_params = self.client.get(f"{FLIGHT_URL}")
        serializer_without_params = (
            FlightListSerializer(flights_without_params, many=True)
        )
        self.assertEqual(
            serializer_with_params.data,
            result_with_params.data["results"]
        )
        self.assertEqual(
            serializer_without_params.data,
            result_without_params.data["results"]
        )

    def test_retrieve_flight(self):
        url = flight_detail_url(self.flight1.id)
        result = self.client.get(url)
        result.data.pop("num_available_seats")
        serializer = FlightRetrieveSerializer(self.flight1)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_flight(self):
        result = self.client.post(FLIGHT_URL)
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
        self.airport1 = sample_airport()
        self.airport2 = sample_airport(name="test_airport2")
        self.route1 = sample_route(
            source=self.airport1,
            destination=self.airport2
        )
        self.airplane = sample_airplane()

    def test_admin_create_flight(self):
        data_flight = {
            "route": self.route1.id,
            "airplane": self.airplane.id,
            "departure_time": datetime(2025, 2, 2, 12, 2),
            "arrival_time": datetime(2025, 2, 2, 14, 2)
        }
        result = self.client.post(FLIGHT_URL, data_flight)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
