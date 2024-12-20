from rest_framework import serializers

from .models import Booking, Product, Trip


class ProductSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.name")

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "created_at",
            "updated_at",
            "company_name",
        ]
        read_only_fields = ["created_at", "updated_at"]


class TripSerializer(serializers.ModelSerializer):
    booked_pax = serializers.ReadOnlyField()
    available_pax = serializers.ReadOnlyField()
    has_space = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()

    class Meta:
        model = Trip
        fields = [
            "id",
            "product",
            "start_date",
            "end_date",
            "max_pax",
            "booked_pax",
            "available_pax",
            "has_space",
            "is_full",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "trip",
            "pax",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
