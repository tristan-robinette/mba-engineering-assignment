from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce

from .models import Trip, Booking, Product, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ("sender", "content", "parent_message", "timestamp")
    readonly_fields = (
        "sender",
        "content",
        "parent_message",
        "timestamp",
    )
    show_change_link = False


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ("pax", "status", "created_at")
    readonly_fields = ("created_at",)
    can_delete = False
    show_change_link = True


class BookingStatusFilter(SimpleListFilter):
    title = "Booking Status"
    parameter_name = "booking_status"

    def lookups(self, request, model_admin):
        return [
            ("no_bookings", "No Bookings"),
            ("partially_booked", "Partially Booked"),
            ("fully_booked", "Fully Booked"),
            ("at_least_one", "At Least One Booking"),
        ]

    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            booked_pax_total=Coalesce(Sum("booking__pax", filter=F("booking__status") == Value("APPROVED")), 0)
        )
        lookup = self.value()

        if lookup == "no_bookings":
            return queryset.filter(booked_pax_total=0)
        elif lookup == "partially_booked":
            return queryset.filter(booked_pax_total__gt=0, booked_pax_total__lt=F("max_pax"))
        elif lookup == "fully_booked":
            return queryset.filter(booked_pax_total=F("max_pax"))
        elif lookup == "at_least_one":
            return queryset.filter(booked_pax_total__gt=0)
        return queryset


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "start_date",
        "end_date",
        "max_pax",
        "booked_pax_display",
        "available_pax",
        "has_space",
        "is_full",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "booked_pax_display",
        "available_pax",
        "has_space",
        "is_full",
        "created_at",
        "updated_at",
    )
    inlines = [
        BookingInline,
    ]
    search_fields = ("product_id",)
    list_filter = ("product", BookingStatusFilter)
    ordering = ("start_date",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            booked_pax_total=Coalesce(
                Sum("booking__pax", filter=F("booking__status") == Value("APPROVED")), 0)
        )

    def booked_pax_display(self, obj):
        return obj.booked_pax_total

    booked_pax_display.admin_order_field = "booked_pax_total"
    booked_pax_display.short_description = "Booked Pax"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("trip", "pax", "status", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    list_filter = ("status", "trip__product")
    search_fields = ("trip__product_id",)
    raw_id_fields = ("trip",)
    inlines = [
        MessageInline,
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "price", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "sender",
        "booking",
        "parent_message",
        "replies",
        "booking",
        "timestamp",
    )
    readonly_fields = ("timestamp",)
    search_fields = ("sender", "content")
    ordering = ("timestamp",)
    raw_id_fields = ("booking", "parent_message")

    def replies(self, obj):
        return obj.replies.count()
