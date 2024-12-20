from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Trip, Booking, Product
from .serializers import TripSerializer, BookingSerializer, ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all().order_by("start_date")
    serializer_class = TripSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product"]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["trip"]
