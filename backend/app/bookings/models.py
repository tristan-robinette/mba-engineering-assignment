from django.core.exceptions import ValidationError
from django.db import models
from datetime import date


MININUM_MAX_PAX = 1


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey("companies.Company", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Trip(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    max_pax = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name}: {self.start_date}—{self.end_date}"

    @property
    def booked_pax(self):
        return sum(
            booking.pax
            for booking in self.booking_set.filter(status="APPROVED")
        )

    @property
    def available_pax(self):
        return self.max_pax - self.booked_pax

    @property
    def has_space(self):
        return self.available_pax > 0

    @property
    def is_full(self):
        return self.booked_pax >= self.max_pax

    def clean(self):
        if self.start_date < date.today():
            raise ValidationError({'start_date': "The start date cannot be in the past."})
        if self.start_date > self.end_date:
            raise ValidationError({
                'start_date': "The start date cannot be later than the end date.",
                'end_date': "The end date cannot be earlier than the start date."
            })
        if self.max_pax < MININUM_MAX_PAX:
            raise ValidationError({'max_pax': 'max_pax should have a value of at least 1.'})

    def save(self, *args, **kwargs):
        # Django REST does not call 'full_clean' in ModelSerializers
        # so adding here but usually this would go in a service
        # layer.
        self.full_clean()
        super().save(*args, **kwargs)


class Booking(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    pax = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=100,
        choices=[
            ("PENDING", "PENDING"),
            ("APPROVED", "APPROVED"),
            ("REJECTED", "REJECTED"),
        ],
        default="PENDING",
    )

    def approve_booking(self):
        if self.status != "APPROVED":
            self.status = "APPROVED"
            self.save(update_fields=["status"])
        return self

    def clean(self):
        if not self.pk and self.status == "APPROVED":
            raise ValidationError({'status': "Booking status should be 'PENDING' or 'REJECTED' upon creation."})

    def save(self, *args, **kwargs):
        # Django REST does not call 'full_clean' in ModelSerializers
        # so adding here but usually this would go in a service
        # layer.
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.trip}: {self.pax} / {self.status}"


class Message(models.Model):
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="messages"
    )
    parent_message = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=100)

    def __str__(self):
        return f"Message by {self.sender} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ["timestamp"]
