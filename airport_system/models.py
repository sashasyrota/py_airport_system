from django.db import models
from django.db.models import CASCADE

from user.models import User


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
    user = User