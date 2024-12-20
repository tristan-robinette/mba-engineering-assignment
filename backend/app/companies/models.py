from bookings.models import Booking
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def total_bookings(self):
        return Booking.objects.filter(trip__product__company=self).count()
