

# Install

The code will run on Docker or locally. Up to you.

## Docker

1. Start up

```bash
$ docker compose up
```

2. Django Set up (with docker up continuing to run in another terminal)

```bash
$ docker compose exec django python manage.py migrate
$ docker compose exec django python manage.py createsuperuser
$ docker compose exec django python manage.py seed 200 
# ^ This will seed the application with 200 products and a large range of Trips and Bookings.
```

3. Goto the admin panel

   Visit <http://127.0.0.1:8000/admin> and login using the credentials you entered when you created the superuser.



## Local install

Prerequisites: Built using Python 3.12. The database is SQLite.

1. Set up your environment

```bash
$ cd ./backend
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

2. Set up the Django application

```bash
$ cd ./backend/app
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py seed 200 # This will seed the application with 200 products and a large range of Trips and Bookings.
```

3. Start the application

```bash
$ cd ./backend/app
$ python manage.py runserver
```

4. Goto the admin panel

   Visit <http://127.0.0.1:8000/admin> and login using the credentials you entered when you created the superuser.