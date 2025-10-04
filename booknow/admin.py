from django.contrib import admin
from .models import ServiceCategory, Service, Booking
from .templatetags.money import aud_cents

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    list_editable = ("sort_order",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "base_price")
    list_filter = ("category",)
    search_fields = ("name", "slug", "category__name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category",)
    ordering = ("category__sort_order", "name")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id","service","name","email","preferred_date","frequency","status","price_estimate_display","created_at")
    list_filter  = ("status","frequency","service","preferred_date")
    search_fields = ("name","email","phone","service__name")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    def price_estimate_display(self, obj):
        return aud_cents(obj.price_estimate) if obj.price_estimate is not None else ""
    price_estimate_display.short_description = "Estimate"


    fieldsets = (
        ("Service", {"fields": ("service","status","price_estimate")}),
        ("Customer", {"fields": ("name","email","phone")}),
        ("Address", {"fields": ("address_line","suburb","state","postcode")}),
        ("Schedule", {"fields": ("preferred_date","preferred_time","frequency","access_window")}),
        ("Details", {"fields": ("details", "parking_notes")}),
        ("Tracking", {"fields": ("created_at","updated_at")}),
    )





