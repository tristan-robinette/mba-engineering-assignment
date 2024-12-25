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

    def get_queryset(self):
        # get the longest possible path to prefetch for this queryset.
        # Suppose you have a message with 4 levels of reply nesting
        # This queryset would prefetch 'messages__replies__replies__replies__replies'
        queryset = super().get_queryset()
        prefetch_paths = []
        current_path = "messages__replies"
        while queryset.filter(**{f"{current_path}__isnull": False}).exists():
            prefetch_paths.append(current_path)
            current_path += "__replies"
        return queryset.prefetch_related(*prefetch_paths)
