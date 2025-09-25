# from django.shortcuts import render

# Create your views here.

# I added this line downward



from django.shortcuts import render
from crm.models import Service

from django.shortcuts import get_object_or_404
from crm.models import Service


def home(request):
    services = Service.objects.filter(is_active=True)[:8]
    return render(request, "website/home.html", {"services": services})


def services(request):
    items = Service.objects.filter(is_active=True).order_by('name')
    return render(request, "website/services.html", {"services": items})




# ====================================================================================================
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .forms import ContactForm
from crm.models import Customer, Activity

RATE_WINDOW_SECONDS = 600  # 10 minutes
RATE_MAX_SUBMITS = 3

def contact(request):
    # Simple session rate-limit
    now = timezone.now().timestamp()
    last = request.session.get("contact_last_ts", 0)
    count = request.session.get("contact_count", 0)
    if now - last > RATE_WINDOW_SECONDS:
        count = 0  # reset window

    if request.method == "POST":
        form = ContactForm(request.POST)
        if count >= RATE_MAX_SUBMITS:
            form.add_error(None, "Too many submissions. Please try again later.")
        if form.is_valid():
            data = form.cleaned_data

            # Upsert Customer by email (fallback: phone)
            lookup = {"email": data["email"]}
            defaults = {
                "full_name": data["name"],
                "phone": data.get("phone"),
                "notes": f"Contact form subject: {data['subject']}",
                "suburb": None,
            }
            customer, created = Customer.objects.get_or_create(defaults=defaults, **lookup)
            if not created:
                # update basic fields
                customer.full_name = data["name"]
                if data.get("phone"):
                    customer.phone = data["phone"]
                customer.save()

            # Log Activity
            Activity.objects.create(
                customer=customer,
                request=None,
                type="email",
                message=f"[{data['subject']}] {data['message']}",
                created_by=None,
            )

            # Send emails (console backend in dev)
            admin_body = (
                f"New contact enquiry\n\n"
                f"Name: {data['name']}\n"
                f"Email: {data['email']}\n"
                f"Phone: {data.get('phone') or '-'}\n"
                f"Subject: {data['subject']}\n\n"
                f"Message:\n{data['message']}\n"
            )
            send_mail(
                subject="Website Contact Enquiry",
                message=admin_body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "admin@localhost"),
                recipient_list=[getattr(settings, "DEFAULT_FROM_EMAIL", "admin@localhost")],
                fail_silently=True,
            )
            send_mail(
                subject="We received your enquiry",
                message="Thanks for contacting B&T Bright Spotless. We’ll get back to you shortly.",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "admin@localhost"),
                recipient_list=[data["email"]],
                fail_silently=True,
            )

            # Update rate-limit window
            request.session["contact_last_ts"] = now
            request.session["contact_count"] = count + 1

            return redirect("/contact/?sent=1")
        else:
            # update rate window on failed attempts too
            request.session["contact_last_ts"] = now
            request.session["contact_count"] = count + 1
    else:
        form = ContactForm()

    sent = request.GET.get("sent") == "1"
    return render(request, "website/contact.html", {"form": form, "sent": sent})

def about(request):
    return render(request, "website/about.html")


from django.templatetags.static import static

def portfolio(request):
    items = [
        {
            "image": static("images/apartment_portfolio.webp"),
            "service": "end-of-lease",
            "title": "End of Lease",
            "caption": "Kitchen & living deep clean",
        },
        {
            "image": static("images/new_building_portfolio.webp"),
            "service": "new-build",
            "title": "New Build",
            "caption": "Fine dust removal & polish",
        },
        {
            "image": static("images/residential_portfolio.webp"),
            "service": "residential",
            "title": "Residential",
            "caption": "Bedroom & carpet freshening",
        },
        {
            "image": static("images/gym_portfolio.webp"),
            "service": "gym",
            "title": "Gym Cleaning",
            "caption": "Equipment sanitisation & floor polish",
        },
        {
            "image": static("images/bus_portfolio.webp"),
            "service": "bus",
            "title": "Bus Cleaning",
            "caption": "Deep interior vehicle cleaning",
        },
        {
            "image": static("images/child_cleaning_portfolio.webp"),
            "service": "child-care",
            "title": "Child Care",
            "caption": "Playroom disinfection & toy sanitising",
        },
        {
            "image": static("images/medical_cleaning_portfolio.webp"),
            "service": "medical",
            "title": "Medical",
            "caption": "Sterile clinic & surgery space cleaning",
        },
    ]
    return render(request, "website/portfolio.html", {"portfolio_items": items})


def service_detail(request, slug):
    svc = get_object_or_404(Service, slug=slug, is_active=True)
    # parse inclusions into a list (supports comma or newline separated)
    inclusions = []
    if svc.inclusions:
        raw = svc.inclusions.replace("\r", "")
        inclusions = [i.strip(" -•\t") for i in raw.replace(",", "\n").split("\n") if i.strip()]
    return render(request, "website/service_detail.html", {"svc": svc, "inclusions": inclusions})
