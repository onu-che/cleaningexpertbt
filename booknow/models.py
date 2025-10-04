from django.db import models
from django.utils import timezone

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "name")
        verbose_name_plural = "Service categories"

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name="services")
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    blurb = models.TextField(blank=True)
    hero_image = models.URLField(blank=True)  # can switch to ImageField later
    base_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        ordering = ("category__sort_order", "name")

    def __str__(self):
        return self.name


class Booking(models.Model):
    FREQ_ONE = "one_time"
    FREQ_WEEKLY = "weekly"
    FREQ_FN = "fortnightly"
    FREQ_MONTHLY = "monthly"
    FREQ_CHOICES = [
        (FREQ_ONE, "One-time"),
        (FREQ_WEEKLY, "Weekly"),
        (FREQ_FN, "Fortnightly"),
        (FREQ_MONTHLY, "Monthly"),

    ]

    ST_NEW = "new"
    ST_CONF = "confirmed"
    ST_DONE = "completed"
    ST_CANCEL = "cancelled"
    STATUS_CHOICES = [
        (ST_NEW, "New"),
        (ST_CONF, "Confirmed"),
        (ST_DONE, "Completed"),
        (ST_CANCEL, "Cancelled"),
    ]

    # Core
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="bookings")

    # Contact
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40)

    # AU Address
    address_line = models.CharField(max_length=200)
    suburb = models.CharField(max_length=120)
    state = models.CharField(max_length=10)      # e.g., NSW, VIC...
    postcode = models.CharField(max_length=10)   # keep as char to preserve leading zeros

    # Dynamic service-specific details (JSON)
    details = models.JSONField(default=dict, blank=True)

    # Schedule
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    frequency = models.CharField(max_length=20, choices=FREQ_CHOICES, default=FREQ_ONE)

    # Workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ST_NEW)

    # Parking + Availability.
    parking_notes = models.CharField(max_length=200, blank=True)
    access_window = models.CharField(
        max_length=100, blank=True,
        help_text="e.g., 8–10am window or 'after 5pm'."
    )

    # Estimated price in cents (so $123.45 = 12345)
    price_estimate = models.IntegerField(null=True, blank=True, help_text="Estimated price in cents")

    # Tracking
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["service"]),
        ]

    def __str__(self):
        return f"#{self.pk} {self.service.name} · {self.name} · {self.suburb}"



