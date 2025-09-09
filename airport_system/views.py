from django.db.models import Func, F, Value
from rest_framework import viewsets

from airport_system.models import Crew, Airport, Route, Order, AirplaneType, Airplane, Flight, Ticket
from airport_system.serializers import CrewSerializer, AirportSerializer, RouteSerializer, OrderSerializer, \
    AirplaneTypeSerializer, AirplaneSerializer, FlightSerializer, RouteListSerializer, FlightListSerializer, \
    AirplaneListSerializer, RouteRetrieveSerializer, OrderListSerializer, AirplaneRetrieveSerializer, \
    OrderRetrieveSerializer


class CrewViewSet(viewsets.ModelViewSet):
    serializer_class = CrewSerializer
    queryset = Crew.objects.all()


class AirportViewSet(viewsets.ModelViewSet):
    serializer_class = AirportSerializer
    queryset = Airport.objects.all()


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.none()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = Route.objects.all()
        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.none()

    def get_queryset(self):
        if self.action in ("list", "retrieve"):
            return Order.objects.all().prefetch_related("tickets__flight__route__source", "tickets__flight__route__destination")
        return Order.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        elif self.action == "retrieve":
            return OrderRetrieveSerializer
        return OrderSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AirplaneTypeSerializer
    queryset = AirplaneType.objects.all()


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.none()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer

    def get_queryset(self):
        queryset = Airplane.objects.all()
        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.none()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        return FlightSerializer

    def get_queryset(self):
        queryset = Flight.objects.all()
        if self.action in ("list", "retrieve"):
            return (
                queryset
                .select_related("route__destination", "route__source", "airplane")
                .annotate(
                    source_destination=Func(
                        F("route__source__name"),
                        Value(" - "),
                        F("route__destination__name"),
                        function="CONCAT"
                    )
                )
            )

        return queryset
