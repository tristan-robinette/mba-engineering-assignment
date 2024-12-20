from datetime import date

from companies.models import Company
from django.test import TestCase

from ..models import Booking, Product, Trip


class TripModelTest(TestCase):
    def setUp(self):
        company = Company.objects.create(name="Test Company")
        product = Product.objects.create(
            name="Test Product",
            description="Test Product Description",
            price=100.00,
            company=company,
        )
        # Create a Trip instance
        self.trip = Trip.objects.create(
            product=product,
            start_date=date(2024, 1, 10),
            end_date=date(2024, 1, 20),
            max_pax=10,
        )

    def test_booked_pax_no_bookings(self):
        # With no bookings, booked_pax should be 0
        self.assertEqual(self.trip.booked_pax, 0)

    def test_booked_pax_with_approved_bookings(self):
        # Add approved bookings
        Booking.objects.create(trip=self.trip, pax=3, status="APPROVED")
        Booking.objects.create(trip=self.trip, pax=2, status="APPROVED")
        # Total should be 5 (3 + 2)
        self.assertEqual(self.trip.booked_pax, 5)

    def test_booked_pax_with_mixed_status_bookings(self):
        # Add mixed-status bookings
        Booking.objects.create(trip=self.trip, pax=4, status="APPROVED")
        Booking.objects.create(trip=self.trip, pax=3, status="PENDING")
        Booking.objects.create(trip=self.trip, pax=2, status="REJECTED")
        # Only the approved one should count
        self.assertEqual(self.trip.booked_pax, 4)

    def test_available_pax_no_bookings(self):
        # When no bookings, available_pax should be max_pax
        self.assertEqual(self.trip.available_pax, 10)

    def test_available_pax_with_approved_bookings(self):
        # Add approved bookings
        Booking.objects.create(trip=self.trip, pax=6, status="APPROVED")
        self.assertEqual(self.trip.available_pax, 4)  # max_pax - booked_pax

    def test_has_space_true(self):
        # Add a booking to ensure available_pax is > 0
        Booking.objects.create(trip=self.trip, pax=8, status="APPROVED")
        self.assertTrue(self.trip.has_space)

    def test_has_space_false_when_full(self):
        # Fill the trip to capacity
        Booking.objects.create(trip=self.trip, pax=10, status="APPROVED")
        self.assertFalse(self.trip.has_space)

    def test_is_full_true_when_exact_capacity(self):
        # Fill trip to exact capacity
        Booking.objects.create(trip=self.trip, pax=10, status="APPROVED")
        self.assertTrue(self.trip.is_full)

    def test_is_full_false_when_not_full(self):
        # Bookings are below max_pax
        Booking.objects.create(trip=self.trip, pax=5, status="APPROVED")
        self.assertFalse(self.trip.is_full)
