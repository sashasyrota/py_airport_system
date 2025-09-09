from django.db.models import Func, F, Value
from django.db.models.aggregates import Count
from rest_framework import viewsets

from airport_system.models import Crew, Airport, Route, Order, AirplaneType, Airplane, Flight, Ticket
from airport_system.serializers import CrewSerializer, AirportSerializer, RouteSerializer, OrderSerializer, \
    AirplaneTypeSerializer, AirplaneSerializer, FlightSerializer, RouteListSerializer, FlightListSerializer, \
     RouteRetrieveSerializer, OrderListSerializer, \
    OrderRetrieveSerializer, FlightRetrieveSerializer


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

    @staticmethod
    def str_to_list(str_data: str) -> list:
        return [int(data) for data in (str_data.split(","))]

    def get_serializer_class(self):
        return AirplaneSerializer

    def get_queryset(self):
        airplane_types = self.request.query_params.get("airplane_types")
        if airplane_types:
            queryset = Airplane.objects.filter(airplane_type__in=AirplaneViewSet.str_to_list(airplane_types))
        else:
            queryset = Airplane.objects.all()

        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.none()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    def get_queryset(self):
        source_airport = self.request.query_params.get("source_airport")
        destination_airport = self.request.query_params.get("destination_airport")
        queryset = Flight.objects.all()
        if source_airport:
            queryset = queryset.filter(route__source__in=AirplaneViewSet.str_to_list(source_airport))
        if destination_airport:
            queryset = queryset.filter(route__destination__in=AirplaneViewSet.str_to_list(destination_airport))


        if self.action in ("list", "retrieve"):
            return (
                queryset
                .select_related("route__destination", "route__source", "airplane")
                .annotate(
                    num_available_seats=F("airplane__rows") * F("airplane__seats_in_row") - Count("ticket")
                )
            )

        return queryset
