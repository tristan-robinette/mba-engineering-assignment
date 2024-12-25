from rest_framework import serializers

from .models import Booking, Product, Trip, Message


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


class MessageSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "content", "timestamp", "sender", "replies"]

    def get_replies(self, instance):
        return MessageSerializer(instance.replies, many=True, context=self.context).data


class BookingSerializer(serializers.ModelSerializer):
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
