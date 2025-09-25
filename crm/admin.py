# Register your models here.

from django.contrib import admin
from .models import Customer, Service, Request, Activity


class ActivityInline(admin.TabularInline): #added 
    model = Activity
    extra = 0
    readonly_fields = ("created_at", "created_by")
    fields = ("type", "message", "created_by", "created_at")

class RequestInline(admin.TabularInline):
    model = Request
    extra = 0
    readonly_fields = ("created_at", "updated_at")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "suburb", "created_at")
    search_fields = ("full_name", "email", "phone", "suburb")
    inlines = [RequestInline]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "base_price", "duration_minutes", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description", "short_blurb")
    readonly_fields = ("slug",)
    fieldsets = (
        ("Basics", {
            "fields": ("name", "slug", "description", "short_blurb", "inclusions", "hero_image")
        }),
        ("Pricing & Duration", {
            "fields": ("base_price", "duration_minutes", "is_active")
        }),
        ("SEO", {
            "fields": ("seo_title", "seo_description")
        }),
    )


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("customer", "service", "status", "preferred_date", "assigned_staff", "created_at")
    list_filter = ("status", "preferred_date", "service")
    search_fields = ("customer__full_name", "customer__email", "customer__phone")
    inlines = [ActivityInline]  # <-- added new 


    actions = ["mark_scheduled", "mark_completed", "mark_cancelled"]

    def mark_scheduled(self, request, queryset):
        queryset.update(status="scheduled")
    mark_scheduled.short_description = "Mark selected as Scheduled"

    def mark_completed(self, request, queryset):
        queryset.update(status="completed")
    mark_completed.short_description = "Mark selected as Completed"

    def mark_cancelled(self, request, queryset):
        queryset.update(status="cancelled")
    mark_cancelled.short_description = "Mark selected as Cancelled"


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("customer", "request", "type", "created_by", "created_at")
    list_filter = ("type",)
    readonly_fields = ("created_at",)
