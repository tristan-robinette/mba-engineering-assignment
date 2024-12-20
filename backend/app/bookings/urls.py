from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, BookingViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet)
router.register(r"trips", TripViewSet)
router.register(r"bookings", BookingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
