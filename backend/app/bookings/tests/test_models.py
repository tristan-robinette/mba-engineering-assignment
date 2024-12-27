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

    def test_trip_max_max_has_capacity(self):
        self.trip.max_pax = 0
        with self.assertRaises(ValidationError) as context:
            self.trip.save()

        self.assertIn('max_pax', context.exception.error_dict)

        self.assertEqual(
            context.exception.error_dict['max_pax'][0].message,
            "max_pax should have a value of at least 1."
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

    def test_trip_start_date_later_than_end_date(self):
        self.trip.start_date = date.today().replace(day=10, month=12, year=YEAR_IN_FUTURE)
        self.trip.end_date = date.today().replace(day=5, month=12, year=YEAR_IN_FUTURE)

        with self.assertRaises(ValidationError) as context:
            self.trip.save()

        self.assertIn('start_date', context.exception.error_dict)
        self.assertIn('end_date', context.exception.error_dict)
        self.assertEqual(
            context.exception.error_dict['start_date'][0].message,
            "The start date cannot be later than the end date."
        )
        self.assertEqual(
            context.exception.error_dict['end_date'][0].message,
            "The end date cannot be earlier than the start date."
        )

    def test_booked_pax_no_bookings(self):
        # With no bookings, booked_pax should be 0
        self.assertEqual(self.trip.booked_pax, 0)

    def test_booked_pax_with_approved_bookings(self):
        # Add approved bookings
        Booking.objects.create(trip=self.trip, pax=3).approve_booking()
        Booking.objects.create(trip=self.trip, pax=2).approve_booking()
        # Total should be 5 (3 + 2)
        self.assertEqual(self.trip.booked_pax, 5)

    def test_booked_pax_with_mixed_status_bookings(self):
        # Add mixed-status bookings
        Booking.objects.create(trip=self.trip, pax=4).approve_booking()
        Booking.objects.create(trip=self.trip, pax=3, status="PENDING")
        Booking.objects.create(trip=self.trip, pax=2, status="REJECTED")
        # Only the approved one should count
        self.assertEqual(self.trip.booked_pax, 4)

    def test_available_pax_no_bookings(self):
        # When no bookings, available_pax should be max_pax
        self.assertEqual(self.trip.available_pax, 10)

    def test_available_pax_with_approved_bookings(self):
        # Add approved bookings
        Booking.objects.create(trip=self.trip, pax=6).approve_booking()
        self.assertEqual(self.trip.available_pax, 4)  # max_pax - booked_pax

    def test_has_space_true(self):
        # Add a booking to ensure available_pax is > 0
        Booking.objects.create(trip=self.trip, pax=8).approve_booking()
        self.assertTrue(self.trip.has_space)

    def test_has_space_false_when_full(self):
        # Fill the trip to capacity
        Booking.objects.create(trip=self.trip, pax=10).approve_booking()
        self.assertFalse(self.trip.has_space)

    def test_is_full_true_when_exact_capacity(self):
        # Fill trip to exact capacity
        Booking.objects.create(trip=self.trip, pax=10).approve_booking()
        self.assertTrue(self.trip.is_full)

    def test_is_full_false_when_not_full(self):
        # Bookings are below max_pax
        Booking.objects.create(trip=self.trip, pax=5).approve_booking()
        self.assertFalse(self.trip.is_full)

    def test_no_more_space_remaining_in_trip_wont_allow_new_bookings(self):
        with self.assertRaises(ValidationError) as context:
            # trip max is 10 therefore 20 shouldnt be allowed.
            Booking.objects.create(trip=self.trip, pax=20).approve_booking()
        self.assertIn("pax", context.exception.error_dict)
        self.assertEqual(
            context.exception.error_dict['pax'][0].message,
            "Not enough space remaining for this trip."
        )

    def test_trip_has_started_wont_allow_new_bookings(self):
        self.trip.start_date = date(1990, 1, 1)
        with self.assertRaises(ValidationError) as context:
            Booking.objects.create(trip=self.trip, pax=5).approve_booking()
        self.assertIn("trip", context.exception.error_dict)
        self.assertEqual(
            context.exception.error_dict['trip'][0].message,
            "This trip has already started."
        )


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

    def test_booking_is_not_approved_by_default(self):
        with self.assertRaises(ValidationError) as context:
            Booking.objects.create(trip=self.trip, pax=2, status="APPROVED")

        self.assertIn('status', context.exception.error_dict)

        self.assertEqual(
            context.exception.error_dict['status'][0].message,
            "Booking status should be 'PENDING' or 'REJECTED' upon creation."
        )
