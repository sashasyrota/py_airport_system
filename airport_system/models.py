from django.db import models
from django.db.models import CASCADE
from django.db.models.constraints import UniqueConstraint

from airport.settings import AUTH_USER_MODEL


class Crew(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)


class Airport(models.Model):
    name = models.CharField(max_length=255, unique=True)
    closest_big_city = models.CharField(null=True)

    def __str__(self):
        return f"{self.name} ({self.closest_big_city})"


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=CASCADE, related_name="routes")
    destination = models.ForeignKey(Airport, on_delete=CASCADE)
    distance = models.IntegerField()

    @property
    def source_destination(self):
        return f"{self.source} - {self.destination}"

    def __str__(self):
        return f"{self.source} - {self.destination} ({self.distance} km)"

    class Meta:
        constraints = [
            UniqueConstraint(fields=["source", "destination"], name="unique route")
        ]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = AUTH_USER_MODEL


class AirplaneType(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name

class Airplane(models.Model):
    name = models.CharField()
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=CASCADE)

    def __str__(self):
        return f"{self.name} ({self.airplane_type})"

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{self.route} {self.airplane}, {self.departure_time} - {self.arrival_time}"



class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=CASCADE)
    order = models.ForeignKey(Order, on_delete=CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            UniqueConstraint(fields=["row", "seat", "flight"], name="unique seats for flight")
        ]