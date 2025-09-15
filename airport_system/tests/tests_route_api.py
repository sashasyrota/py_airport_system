from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from rest_framework.test import APIClient

from airport_system.models import Route
from airport_system.serializers import RouteListSerializer, RouteRetrieveSerializer
from airport_system.tests.tests_airport_api import sample_airport
from user.models import User

ROUTE_LIST = reverse("airport_system:route-list")

def sample_route(**params):
    defaults = {
        "source": None,
        "destination": None,
        "distance": 100
    }
    defaults.update(params)
    return Route.objects.create(**defaults)

def route_detail_url(route_id: int):
    return reverse("airport_system:route-detail", args=(route_id,))


class UnauthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(ROUTE_LIST)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test", password="testtest")
        self.client.force_authenticate(self.user)
        self.airport1 = sample_airport()
        self.airport2 = sample_airport(name="test_airport2")
        self.route1 = sample_route(source=self.airport1, destination=self.airport2)

    def test_route_list(self):
        result = self.client.get(ROUTE_LIST)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data["results"], serializer.data)

    def test_route_detail(self):
        url = route_detail_url(self.route1.id)
        result = self.client.get(url)
        serializer = RouteRetrieveSerializer(self.route1)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_route(self):
        result = self.client.post(ROUTE_LIST)
        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)



class AdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(email="admin_test", password="admin_testtest", is_staff=True)
        self.client.force_authenticate(self.admin_user)
        self.airport1 = sample_airport()
        self.airport2 = sample_airport(name="test_airport2")

    def test_admin_create_route(self):
        data_route = {
        "source": self.airport1.id,
        "destination": self.airport2.id,
        "distance": 100
    }
        result = self.client.post(ROUTE_LIST, data_route)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
