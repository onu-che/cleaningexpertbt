from django.urls import path
from . import views

urlpatterns = [
    path("", views.service_select, name="booknow_start"),
    path("service/", views.service_select, name="booknow_service"),
    path("details/", views.details, name="booknow_details"),
    path("schedule/", views.schedule, name="booknow_schedule"),
    path("contact/", views.contact, name="booknow_contact"),
    path("review/", views.review, name="booknow_review"),
    path("thank-you/", views.thank_you, name="booknow_thank_you"),
]


