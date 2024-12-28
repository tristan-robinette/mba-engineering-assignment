from rest_framework import serializers

from .models import Booking, Product, Trip, Message
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.serializers import ValidationError


class ValidationMixin:
    """
    Turns DjangoValidationErrors into DRF validation errors to allow for centralizing Model
    logic and constraints in one area.
    """
    def validate(self, data):
        instance = self.Meta.model(**data)
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise ValidationError(e.message_dict)
        return data


class ProductSerializer(ValidationMixin, serializers.ModelSerializer):
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


class TripSerializer(ValidationMixin, serializers.ModelSerializer):
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


class MessageSerializer(ValidationMixin, serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "content", "timestamp", "sender", "replies"]

    def get_replies(self, instance):
        return MessageSerializer(instance.replies, many=True, context=self.context).data


class BookingSerializer(ValidationMixin, serializers.ModelSerializer):
    email_thread = MessageSerializer(many=True, read_only=True, source='messages')

    class Meta:
        model = Booking
        fields = [
            "id",
            "trip",
            "pax",
            "status",
            "created_at",
            "updated_at",
            "email_thread",
        ]
        read_only_fields = ["created_at", "updated_at"]
