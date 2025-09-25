
# I created this file


from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services, name="services"),  # <-- add
    path("contact/", views.contact, name="contact"),  # <-- add
    path("about/", views.about, name="about"),  # <-- add
    path("portfolio/", views.portfolio, name="portfolio"), 
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
]


