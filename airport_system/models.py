from django.db import models
from django.db.models import CASCADE

from airport.settings import AUTH_USER_MODEL


class Crew(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(null=True)


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=CASCADE)


class Order(models.Model):
    created_at = models.DateTimeField()
    user = AUTH_USER_MODEL


class AirplaneType(models.Model):
    name = models.CharField()


class Airplane(models.Model):
    name = models.CharField()
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=CASCADE)


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=CASCADE)
    order = models.ForeignKey(Order, on_delete=CASCADE)