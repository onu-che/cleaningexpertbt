from django.contrib import admin
from .models import ServiceCategory, Service, Booking

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
    list_display = ("id", "created_at", "service", "name", "phone", "status", "frequency")
    list_filter = ("status", "frequency", "service", "created_at")
    search_fields = ("name", "email", "phone", "service__name", "suburb", "postcode")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Service", {"fields": ("service",)}),
        ("Customer", {"fields": ("name", "email", "phone")}),
        ("Address (AU)", {"fields": ("address_line", "suburb", "state", "postcode")}),
        ("Details", {"fields": ("details",)}),
        ("Schedule", {"fields": ("preferred_date", "preferred_time", "frequency")}),
        ("Tracking", {"fields": ("status", "created_at", "updated_at")}),
    )
