from django.db import transaction
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from airport_system.models import Crew, Airport, Route, Order, AirplaneType, Airplane, Flight, Ticket


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "closest_big_city"]


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(read_only=True, slug_field="name")


class RouteRetrieveSerializer(RouteSerializer):
    source = AirportSerializer()
    destination = AirportSerializer()


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["id", "name"]


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "airplane_type", "capacity"]


class AirplaneListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "capacity"]


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(read_only=True, slug_field="name")


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all().select_related())
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.only("id", "name").select_related())

    class Meta:
        model = Flight
        fields = ["id", "route", "departure_time", "airplane", "arrival_time"]


class FlightListSerializer(serializers.ModelSerializer):
    airplane = serializers.SlugRelatedField(read_only=True, slug_field="name")
    source_destination = serializers.CharField(read_only=True)

    class Meta:
        model = Flight
        fields = ["id", "source_destination", "airplane", "departure_time", "arrival_time"]


class FlightRetrieveSerializer(FlightSerializer):
    route = serializers.SlugRelatedField(queryset=Route.objects.all().select_related(), slug_field="source_destination")
    airplane = serializers.SlugRelatedField(queryset=Airplane.objects.only("id", "name").select_related(), slug_field="name")


class FlightTicketSerializer(serializers.ModelSerializer):
    route = serializers.SlugRelatedField(slug_field="source_destination", read_only=True)

    class Meta:
        model = Flight
        fields = ["departure_time", "arrival_time", "route"]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight"]

    def validate(self, attrs):
        data = [
            ["row", attrs["row"], attrs["flight"].airplane.rows],
            ["seat", attrs["seat"], attrs["flight"].airplane.seats_in_row]
        ]
        for attr_name, attr_value, attr_airplane_value in data:
            if attr_value > attr_airplane_value or int(attr_value) < 1:
                raise serializers.ValidationError(f"The specified {attr_name} should be in range 1: {attr_airplane_value}")
        return attrs


class TicketListSerializer(TicketSerializer):
    flight = FlightTicketSerializer()

    class Meta:
        model = Ticket
        fields = ["row", "seat", "flight"]


class TicketRetrieveSerializer(TicketSerializer):
    flight = FlightRetrieveSerializer()


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ["id", "created_at", "tickets"]


    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop('tickets')
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderRetrieveSerializer(OrderSerializer):
    tickets = TicketRetrieveSerializer(many=True, read_only=True)