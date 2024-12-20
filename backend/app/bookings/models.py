from django.db import models


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
