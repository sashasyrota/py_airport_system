from rest_framework import viewsets

from airport_system.models import Crew, Airport, Route, Order, AirplaneType, Airplane, Flight, Ticket
from airport_system.serializers import CrewSerializer, AirportSerializer, RouteSerializer, OrderSerializer, \
    AirplaneTypeSerializer, AirplaneSerializer, FlightSerializer, TicketSerializer


class CrewViewSet(viewsets.ModelViewSet):
    serializer_class = CrewSerializer
    queryset = Crew.objects.all()


class AirportViewSet(viewsets.ModelViewSet):
    serializer_class = AirportSerializer
    queryset = Airport.objects.all()


class RouteViewSet(viewsets.ModelViewSet):
    serializer_class = RouteSerializer
    queryset = Route.objects.all()


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AirplaneTypeSerializer
    queryset = AirplaneType.objects.all()


class AirplaneViewSet(viewsets.ModelViewSet):
    serializer_class = AirplaneSerializer
    queryset = Airplane.objects.all()


class FlightViewSet(viewsets.ModelViewSet):
    serializer_class = FlightSerializer
    queryset = Flight.objects.all()


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()

