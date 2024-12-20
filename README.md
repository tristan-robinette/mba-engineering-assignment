# MBA Engineering Assignment (Platform Team)


## Info

This repo contains a small Django app. It serves up a JSON API for a client application (not included for this test) to consume.

The backend is a Django 5 application. It contains a two apps with some models:

### bookings:
- Product
- Trip
- Booking
- Message

A `Booking` is placed on a `Trip` which represents a specific departure for a `Product`.

A `Message` represents as message sent about a `Booking`. They can be in reply to a previous message, or a top level message.

Each model has an API endpoints created for it using Django REST Framework. Along with a basic Django admin setup.

### companies:
- Company

Each product belongs to a company. The company model currently has just one property: the number of bookings this company has.

### URLs:

Once set up, you should be able to view

- http://127.0.0.1:8000/admin - the Django Admin
- http://127.0.0.1:8000/bookings - the bookings API entry point
- http://127.0.0.1:8000/companies - the companies API entry point

## Further reading

- Please view [install.md](./docs/install.md) for installation instructions
- Please view [tasks.md](./docs/tasks.md) for the tasks to be completed