from django.contrib import admin
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


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "start_date",
        "end_date",
        "max_pax",
        "booked_pax",
        "available_pax",
        "has_space",
        "is_full",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "booked_pax",
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
    list_filter = ("product",)
    ordering = ("start_date",)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("booking_set")


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
