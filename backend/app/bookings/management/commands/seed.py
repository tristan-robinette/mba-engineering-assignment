from bookings.models import Booking, Message, Product, Trip
from companies.models import Company
from django.core.management.base import BaseCommand
from bookings.data_creation import create_companies_and_products, create_trips, create_bookings, create_messages


class Command(BaseCommand):
    help = "Populate the database with N trips and varied booking levels"

    def add_arguments(self, parser):
        parser.add_argument("N", type=int, help="Number of trips to create")

    def handle(self, *args, **options):
        num_products = options["N"]

        Product.objects.all().delete()
        Company.objects.all().delete()

        products = create_companies_and_products(num_products)
        self.stdout.write(f"Created {len(products)} companies and products.")

        trips = create_trips(products)
        self.stdout.write(f"Created {len(trips)} trips.")

        bookings = create_bookings(trips)
        self.stdout.write(f"Created {len(bookings)} bookings.")

        self.stdout.write("Creating messages.")
        create_messages(bookings)
