from datetime import date

from companies.models import Company
from bookings.models import Message, Booking
from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import Booking, Product, Trip


YEAR_IN_FUTURE = 3000


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
            start_date=date(YEAR_IN_FUTURE, 1, 10),
            end_date=date(YEAR_IN_FUTURE, 1, 20),
            max_pax=10,
        )

    def test_trip_start_date_in_the_past(self):
        past_date = date.today().replace(day=1, month=1, year=2000)
        self.trip.start_date = past_date
        with self.assertRaises(ValidationError) as context:
            self.trip.save()
            self.assertIn('start_date', context.exception.error_dict)
            self.assertEqual(
                context.exception.error_dict['start_date'][0].message,
                "The start date cannot be in the past."
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


class BookingModelTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name="Test Company")
        product = Product.objects.create(
            name="Test Product",
            description="Test Product Description",
            price=100.00,
            company=company,
        )

        self.trip = Trip.objects.create(
            product=product,
            start_date=date(YEAR_IN_FUTURE, 1, 1),
            end_date=date(YEAR_IN_FUTURE, 1, 20),
            max_pax=10,
        )

        # Create a booking
        self.booking = Booking.objects.create(trip=self.trip, pax=2, status="PENDING")

        # Create messages with threading
        self.message1 = Message.objects.create(
            booking=self.booking, content="Parent message 1", sender="User1"
        )
        self.reply1 = Message.objects.create(
            booking=self.booking, content="Reply to message 1", sender="User2", parent_message=self.message1
        )
        self.reply2 = Message.objects.create(
            booking=self.booking, content="Reply to reply 1", sender="User3", parent_message=self.reply1
        )
        self.message2 = Message.objects.create(
            booking=self.booking, content="Parent message 2", sender="User1"
        )

    def test_booking_email_thread_structure(self):
        booking = Booking.objects.prefetch_related('messages__replies__replies__replies').get(id=self.booking.id)
        email_thread = booking.messages.all()

        self.assertEqual(email_thread.count(), 4)

        message1 = email_thread.first()
        self.assertEqual(message1.content, "Parent message 1")
        self.assertEqual(message1.replies.count(), 1)

        reply1 = message1.replies.first()
        self.assertEqual(reply1.content, "Reply to message 1")
        self.assertEqual(reply1.replies.count(), 1)

        reply2 = reply1.replies.first()
        self.assertEqual(reply2.content, "Reply to reply 1")
        self.assertEqual(reply2.replies.count(), 0)

    def test_empty_email_thread_for_booking_without_messages(self):
        empty_booking = Booking.objects.create(trip=self.trip, pax=3, status="PENDING")
        email_thread = empty_booking.messages.all()
        self.assertEqual(email_thread.count(), 0)