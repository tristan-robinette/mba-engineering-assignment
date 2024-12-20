## General Instructions

The following 4 tasks are to assess your technical skills. Please complete these as if you were assigned them as part of your day job here at MBA. This means working towards best-practices as you understand them.

- Feel free to use Google, SO, ChatGPT, or any other public tools you’re used to using in your workflow.
- Overall quality, structure, and cleanliness of code will be a factor, so don’t rush it.
- Use of version control will also be reviewed.

## Timing
We've designed this test to take around _**4 hours**_.

We'd prefer you to prioritise finishing all the tasks and deliverying a finished product. If there's anywhere you'd have liked to have spent more time, leave a TODO, and we can discuss it in the follow-up interview.

# The Tasks

## 1: API Enhancement

Add a `message_thread` attibute to the `Booking` api endpoint. The messages should be in order and threaded such that each `message` instance has a `replies` attribute containing zero or more replies to it. This should go as deep as the  messages in the model go.

---

## 2: User Stories

Here are some user-stories regarding the API:

> As a product manager,
I want to prevent trips from being created with a start date in the past,
so that customers can only book trips that are still valid and available.

> As a product manager,
I want to ensure that a trip’s `start_date` cannot be later than its `end_date`,
so that trips are defined with valid timelines.

> As a product manager,
I want to enforce that trips have a `max_pax` value of at least 1,
so that trips are not created with invalid capacity.

> As an operations manager,
I want to prevent bookings from being created as `“APPROVED”` by default,
so that the system can enforce approval workflows for all new bookings.

> As an operations manager,
I want to prevent bookings from being approved if the trip is either fully booked or has started in the past,
so that only valid bookings are approved.

> As a customer,
I want to be prevented from creating a `booking` for a `trip` that has already ended,
so that I don’t mistakenly book unavailable trips.


### Instructions:

**Objective:** 

Implement the business logic for each user story and ensure corresponding API endpoints return the appropriate error messages when constraints are violated.

**Deliverables:**
- A working implementation of the logic in the Django backend.
- Automated tests (unit or integration) to verify the acceptance criteria for each user story.

**Constraints:**
- Follow Django best practices for model validations, serializers, and view logic.
- Use the Django Rest Framework for API endpoints.

--- 

## 3: Admin Enhancements

Our Operations team have requested a few upgrades to the UX of the admin:
  1. They would like to order the Trips admin list by Booked Pax (ascending and descending)
  2. They would like to be able to filter trips with the following criteria: No Bookings / Partially Booked / Fully Booked / At Least One Booking

## 4: Code Refactor

I'm sure you'll agree, the [code](../backend/app/bookings/management/commands/seed.py) to seed the DB is quite a mess ! Please refactor it to make it easier to understand, extensible and potentially useful outside of the `seed` command (e.g. we might want to use some of the functionality for E2E or performance testing one day).
