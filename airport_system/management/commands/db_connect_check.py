import time

from django.core.management import BaseCommand, CommandError
from django.db import connection, OperationalError


class Command(BaseCommand):
    help = "Checking database connection"


    def handle(self, *args, **options):
        sec = 0
        while sec < 10:
            try:
                connection.ensure_connection()
                break
            except OperationalError:
                time.sleep(1)
                sec += 1
