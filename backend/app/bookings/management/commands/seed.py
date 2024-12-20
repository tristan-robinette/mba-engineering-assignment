import random
from datetime import timedelta

from bookings.models import Booking, Message, Product, Trip
from companies.models import Company
from django.core.management.base import BaseCommand
from django.utils import timezone


def isAncestor(possible_ancestor, message):
    """Check if `possible_ancestor` is an ancestor of `message`."""
    check_ancestor = lambda current: (
        True
        if current.parent_message == possible_ancestor
        else check_ancestor(current.parent_message)
        if current.parent_message is not None
        else False
    )
    return check_ancestor(message)


def makeRandomString():
    subjects = [
        "The cat",
        "A traveler",
        "The engineer",
        "An artist",
        "The CEO",
        "A programmer",
    ]
    verbs = [
        "jumps over",
        "analyzes",
        "creates",
        "improves",
        "builds",
        "envisions",
    ]
    objects = [
        "a bridge",
        "the code",
        "a masterpiece",
        "a new startup",
        "the solution",
        "a challenge",
    ]
    adjectives = [
        "quickly",
        "efficiently",
        "creatively",
        "with precision",
        "with passion",
        "with curiosity",
    ]

    s = random.choice(subjects)
    v = random.choice(verbs)
    o = random.choice(objects)
    a = random.choice(adjectives)

    return f"{s} {v} {o} {a}."


class Command(BaseCommand):
    help = "Populate the database with N trips and varied booking levels"

    def add_arguments(self, parser):
        parser.add_argument("N", type=int, help="Number of trips to create")

    def handle(self, *args, **options):
        n = options["N"]
        status_choices = ["PENDING", "APPROVED", "REJECTED"]
        p_list = []
        t = []
        b_list = []

        Product.objects.all().delete()
        Company.objects.all().delete()

        for x in range(n):
            c_i = x // 20
            c, _ = Company.objects.get_or_create(
                name=f"Test Company {c_i}",
                description="Lorem ipsum dolor sit amet",
            )
            prod = Product(name=f"Product {x}", description="Lorem ipsum dolor sit amet", price=random.randint(100, 1000), company=c)
            p_list.append(prod)

        Product.objects.bulk_create(p_list)

        p_list = Product.objects.all()

        for prod in p_list:
            pax_limit = random.randint(5, 20)
            duration = timedelta(days=random.randint(1, 14))
            number_of_trips = random.randint(50, 100)
            for trip in range(number_of_trips):
                start = timezone.now().date() + timedelta(
                    days=random.randint(1, 365)
                )
                end = start + duration
                t.append(
                    Trip(
                        product=prod,
                        start_date=start,
                        end_date=end,
                        max_pax=pax_limit,
                    )
                )

        Trip.objects.bulk_create(t)

        trips = Trip.objects.all()

        for t in trips:
            leave_empty = random.random() > 0.3

            if leave_empty:
                continue

            pax_count = 0
            while True:
                pax_to_add = random.randint(1, t.max_pax)
                if pax_count + pax_to_add > t.max_pax:
                    break
                b_list.append(
                    Booking(
                        trip=t,
                        pax=pax_to_add,
                        status=random.choice(status_choices),
                    )
                )
                pax_count += pax_to_add

        for b in b_list:
            b.save()

        bookings = Booking.objects.all()

        for b in bookings[:n]:
            messages = [
                Message(
                    booking=b,
                    content=makeRandomString(),
                    sender=random.choice(["user", "admin"]),
                )
                for _ in range(random.randint(20, 50))
            ]
            msg_list = Message.objects.bulk_create(messages)
            for m in msg_list:
                if random.random() < 0.5:
                    parent = random.choice(msg_list)
                    if parent != m and not isAncestor(m, parent):
                        m.parent_message = parent

            Message.objects.bulk_update(msg_list, ["parent_message"])

        m_list = Message.objects.all()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(p_list)} prods, {len(trips)} trs, {len(b_list)} bks, and {len(m_list)} msgs."
            )
        )
