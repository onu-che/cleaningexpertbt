

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

from django.utils.text import slugify
from django.urls import reverse



class Customer(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address_line = models.CharField(max_length=255, blank=True, null=True)
    suburb = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # SLUG UPDATE========================================================================================
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    hero_image = models.URLField(blank=True, null=True)          # optional, use static or CDN URL
    short_blurb = models.CharField(max_length=160, blank=True)   # for cards/SEO
    inclusions = models.TextField(blank=True, null=True)         # newline- or comma-separated checklist
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)


    # save override
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("service_detail", kwargs={"slug": self.slug})


class Request(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("qualified", "Qualified"),
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    preferred_date = models.DateField()
    preferred_time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    assigned_staff = models.CharField(max_length=100, blank=True, null=True)
    price_quote = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    additional_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer} - {self.service} ({self.status})"


class Activity(models.Model):
    TYPE_CHOICES = [
        ("note", "Note"),
        ("call", "Call"),
        ("email", "Email"),
        ("system", "System"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    request = models.ForeignKey(Request, on_delete=models.SET_NULL, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.customer}"
