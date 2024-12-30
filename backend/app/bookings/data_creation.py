from django.db.models import QuerySet
from faker import Faker
import random
from datetime import timedelta
from django.utils import timezone
from bookings.models import Product, Trip, Booking, Message
from companies.models import Company

fake = Faker()


def generate_conversation(
        num_messages: int = 10,
        participants: tuple = ("user", "admin"),
        max_content_length: int = 200
):
    return [
        {
            "sender": random.choice(participants),
            "content": fake.text(max_nb_chars=max_content_length),
        }
        for _ in range(num_messages)
    ]


def is_ancestor(possible_ancestor: Message, message: Message) -> bool:
    def check_ancestor(current: Message) -> bool:
        if current.parent_message is None:
            return False
        if current.parent_message == possible_ancestor:
            return True
        return check_ancestor(current.parent_message)

    return check_ancestor(message)


def create_companies_and_products(num_products: int, product_price_range: tuple[int, int] = (100, 1000)):
    products = []
    for i in range(num_products):
        c, _ = Company.objects.get_or_create(
            name=f"{fake.name().title()} {i}",
            description=fake.text(max_nb_chars=100)
        )
        product = Product(
            name=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            price=random.randint(*product_price_range),
            company=c,
        )
        products.append(product)

    return Product.objects.bulk_create(products)


def create_trips(products: QuerySet[Product], pax_limit_range: tuple[int, int] = (5, 20), trips_per_product_range: tuple[int, int] = (50, 100)):
    trips = []
    for product in products:
        pax_limit = random.randint(*pax_limit_range)
        duration = timedelta(days=random.randint(1, 14))
        number_of_trips = random.randint(*trips_per_product_range)
        for trip in range(number_of_trips):
            start_date = timezone.now().date() + timedelta(days=random.randint(1, 365))
            end_date = start_date + duration
            trips.append(
                Trip(product=product, start_date=start_date, end_date=end_date, max_pax=pax_limit)
            )

    return Trip.objects.bulk_create(trips)


def create_bookings(trips: QuerySet[Trip], empty_trip_percentage: float = 0.3):
    bookings = []
    status_choices = ["PENDING", "APPROVED", "REJECTED"]

    for trip in trips:
        pax_count = 0
        while random.random() > empty_trip_percentage:
            pax_to_add = random.randint(1, trip.max_pax)
            if pax_count + pax_to_add > trip.max_pax:
                break
            status = random.choice(status_choices)
            set_to_approve = status == "APPROVED"
            booking = Booking(
                trip=trip,
                pax=pax_to_add,
                status="PENDING" if set_to_approve else status,
            )
            booking.save()
            if set_to_approve:
                booking.approve_booking()
            bookings.append(booking)
            pax_count += pax_to_add
    return bookings


def create_messages(
        bookings: QuerySet[Booking],
        messages_per_booking: tuple[int, int] = (20, 50),
        parent_message_percentage: float = 0.5
):
    for booking in bookings:
        conversation = generate_conversation(num_messages=random.randint(*messages_per_booking))
        messages = [
            Message(
                booking=booking,
                content=msg["content"],
                sender=msg["sender"],
            )
            for msg in conversation
        ]
        msg_list = Message.objects.bulk_create(messages)

        for msg in msg_list:
            if random.random() < parent_message_percentage:
                parent_message = random.choice(msg_list)
                if parent_message != msg and not is_ancestor(msg, parent_message):
                    msg.parent_message = parent_message

        Message.objects.bulk_update(msg_list, ["parent_message"])
