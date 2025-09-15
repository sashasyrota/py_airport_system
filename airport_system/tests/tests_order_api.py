from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport_system.models import Order, Ticket
from airport_system.serializers import (
    OrderListSerializer,
    OrderRetrieveSerializer
)
from airport_system.tests.tests_airplane_api import sample_airplane
from airport_system.tests.tests_airport_api import sample_airport
from airport_system.tests.tests_flight_api import sample_flight
from airport_system.tests.tests_route_api import sample_route
from user.models import User

ORDER_URL = reverse("airport_system:order-list")


def sample_order(**params):
    defaults = {
        "user": None
    }
    defaults.update(params)
    return Order.objects.create(**defaults)


def sample_ticket(**params):
    defaults = {
        "row": 1,
        "seat": 1,
        "flight": None,
        "order": None
    }
    defaults.update(params)
    return Ticket.objects.create(**defaults)


def order_detail_url(order_id: int):
    return reverse("airport_system:order-detail", args=(order_id,))


def order_data(**params):
    result = {
        "user": None
    }
    result.update(**params)
    return result


class UnauthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        result = self.client.get(ORDER_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test", password="testtest")
        self.client.force_authenticate(self.user)
        self.order1 = sample_order(user=self.user)
        self.airplane = sample_airplane()
        self.airport1 = sample_airport()
        self.airport2 = sample_airport(name="test_airport2")
        self.route1 = sample_route(
            source=self.airport1,
            destination=self.airport2
        )
        self.flight1 = sample_flight(route=self.route1, airplane=self.airplane)

    def test_flight_order(self):
        result = self.client.get(ORDER_URL)
        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data["results"], serializer.data)

    def test_retrieve_order(self):
        url = order_detail_url(self.order1.id)
        result = self.client.get(url)
        serializer = OrderRetrieveSerializer(self.order1)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_create_order_with_tickets(self):
        tickets_data = [{
            "row": 2,
            "seat": 3,
            "flight": self.flight1.id
        },]
        result = self.client.post(
            ORDER_URL,
            order_data(user=self.user.id, tickets=tickets_data),
            format="json"
        )
        for ticket in result.data["tickets"]:
            for ticket_data in tickets_data:
                for data in ticket_data:
                    self.assertEqual(ticket_data[data], ticket[data])
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    def test_ticket_required(self):
        result = self.client.post(ORDER_URL, order_data(user=self.user.id))
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
