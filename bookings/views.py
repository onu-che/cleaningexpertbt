
# Create your views here.
from django.shortcuts import render, redirect
from .forms import BookingForm
from crm.models import Customer, Request, Activity, Service
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone


from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from .forms import Step1ServiceForm, Step3FrequencyForm, Step4ContactForm



def booking_view(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Selected service (was missing previously)
            svc = data["service"]

            # Check if customer exists or create/update
            customer, created = Customer.objects.get_or_create(
                email=data.get("email"),
                defaults={
                    "full_name": data["full_name"],
                    "phone": data.get("phone"),
                    "address_line": data.get("address_line"),
                    "suburb": data.get("suburb"),
                    "state": data.get("state"),
                    "postcode": data.get("postcode"),
                },
            )
            if not created:
                customer.full_name = data["full_name"]
                customer.phone = data.get("phone")
                customer.address_line = data.get("address_line")
                customer.suburb = data.get("suburb")
                customer.state = data.get("state")
                customer.postcode = data.get("postcode")
                customer.save()

            # Create request (use submitted preferred date/time if provided)
            # Create request (NO price shown to user)
            req = Request.objects.create(
                customer=customer,
                service=svc,
                status="new",
                # Step4ContactForm doesn't have date/time fields, so use safe defaults:
                preferred_date=timezone.localdate(),
                preferred_time=None,
                additional_details=(
                    "Instant Quote (modal) — "
                    f"step2: {session.get('step2', {})}, "
                    f"frequency: {session.get('step3', {})}. "
                    "Preferred date/time not provided in instant-quote modal."
                ),
            )
            # Log activity
            Activity.objects.create(
                customer=customer,
                request=req,
                type="system",
                message="New booking request submitted via website.",
            )

            # Emails
            send_mail(
                "Booking Confirmation",
                f"Thank you {customer.full_name}, we have received your booking.",
                settings.DEFAULT_FROM_EMAIL,
                [customer.email] if customer.email else [],
                fail_silently=True,
            )
            send_mail(
                "New Booking Request",
                f"New booking from {customer.full_name} for {req.service.name} on {req.preferred_date}",
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )

            return redirect("booking_success")
    else:
        initial_service = None
        svc_id = request.GET.get("service")
        if svc_id:
            try:
                initial_service = Service.objects.get(pk=svc_id, is_active=True)
            except Service.DoesNotExist:
                initial_service = None
        form = BookingForm(initial_service=initial_service)

    return render(request, "bookings/booking_form.html", {"form": form})


def booking_success(request):
    return render(request, "bookings/booking_success.html")




# ============================================================================================NEW=======================
# bookings/views.py  — Instant Quote (modal) implementation

from django.conf import settings
from django.core.mail import send_mail

from crm.models import Service, Customer, Request, Activity
from .forms import Step1ServiceForm, Step3FrequencyForm, Step4ContactForm


# ---------- modal template resolver ----------
def _iq_template(request):
    xr = (request.headers.get("X-Requested-With") or "").lower()
    if request.GET.get("dialog") == "1" or xr in ("fetch", "xmlhttprequest"):
        return "bookings/instant_quote_modal_inner.html"
    return "bookings/instant_quote.html"


def _render_iq(request, ctx: dict):
    # ctx MUST be a dict — do NOT pass {...} as a placeholder
    return render(request, _iq_template(request), ctx)


# ---------- service-specific schema for Step 2 ----------
SERVICE_OPTIONS = {
    "residential": {
        "fields": [
            ("bedrooms", forms.IntegerField, {"min_value": 0, "initial": 2, "label": "Bedrooms"}),
            ("bathrooms", forms.IntegerField, {"min_value": 0, "initial": 1, "label": "Bathrooms"}),
            ("has_pets", forms.BooleanField, {"required": False, "label": "Pets at home"}),
            ("oven_clean", forms.BooleanField, {"required": False, "label": "Oven clean add-on"}),
            ("fridge_clean", forms.BooleanField, {"required": False, "label": "Fridge clean add-on"}),
            ("windows_clean", forms.BooleanField, {"required": False, "label": "Windows inside add-on"}),
        ]
    },
    "end-of-lease": {
        "fields": [
            ("bedrooms", forms.IntegerField, {"min_value": 0, "initial": 2, "label": "Bedrooms"}),
            ("bathrooms", forms.IntegerField, {"min_value": 0, "initial": 1, "label": "Bathrooms"}),
            ("steam_clean_carpets", forms.BooleanField, {"required": False, "label": "Steam clean carpets"}),
            ("garage_clean", forms.BooleanField, {"required": False, "label": "Garage sweep & tidy"}),
            ("balcony_clean", forms.BooleanField, {"required": False, "label": "Balcony clean"}),
        ]
    },
    "medical": {
        "fields": [
            ("rooms", forms.IntegerField, {"min_value": 1, "initial": 3, "label": "Treatment rooms"}),
            ("waiting_area", forms.BooleanField, {"required": False, "label": "Waiting area sanitisation"}),
            ("surgery_zone", forms.BooleanField, {"required": False, "label": "Surgery/Procedure room deep clean"}),
            ("autoclave_area", forms.BooleanField, {"required": False, "label": "Autoclave area wipe-down"}),
        ]
    },
    "bus": {
        "fields": [
            ("seats", forms.IntegerField, {"min_value": 1, "initial": 30, "label": "Number of seats"}),
            ("gum_removal", forms.BooleanField, {"required": False, "label": "Gum removal"}),
            ("windows_in_out", forms.BooleanField, {"required": False, "label": "Windows inside & out"}),
            ("exterior_wash", forms.BooleanField, {"required": False, "label": "Exterior wash"}),
        ]
    },
    "_default": {
        "fields": [
            ("area_size", forms.IntegerField, {"min_value": 0, "initial": 100, "label": "Approx area (m²)"}),
            ("windows_clean", forms.BooleanField, {"required": False, "label": "Windows add-on"}),
        ]
    },
}

def get_schema_for(service: Service):
    slug = (service.slug or "").lower()
    for key, schema in SERVICE_OPTIONS.items():
        if key != "_default" and (slug == key or slug.startswith(key)):
            return schema
    return SERVICE_OPTIONS["_default"]

def make_dynamic_form(schema):
    attrs = {}
    for name, field_cls, kwargs in schema["fields"]:
        attrs[name] = field_cls(**kwargs)
    return type("Step2DynamicForm", (forms.Form,), attrs)


# ---------- Instant Quote main view (modal-friendly) ----------
def instant_quote(request):
    """
    4 steps: 1) Service cards  2) Details (dynamic)  3) Frequency  4) Contact
    This returns a fragment when ?dialog=1 (used by the modal).
    """
    session = request.session.get("iq2", {})
    raw_step = request.GET.get("step") or request.POST.get("step") or session.get("step") or 1
    try:
        step = int(raw_step)
    except (TypeError, ValueError):
        step = 1
    step = max(1, min(step, 4))

    # ---------- STEP 1: service selection ----------
    if step == 1:
        form = Step1ServiceForm(initial={"service": session.get("service_id")})
        if request.method == "POST":
            form = Step1ServiceForm(request.POST)
            if form.is_valid():
                session["service_id"] = form.cleaned_data["service"].id
                session["step"] = 2
                request.session["iq2"] = session
                # when modal, caller JS will request the next step; still OK to redirect
                return redirect(f"{request.path}?dialog=1&step=2")
        services = Service.objects.filter(is_active=True).order_by("name")
        return _render_iq(request, {"step": 1, "form": form, "services": services})

    # ensure service chosen
    # ---- recover service_id if missing (e.g., cookies not sent on POST) ----
    if step >= 2 and not session.get("service_id"):
        posted_service = request.POST.get("service") or request.GET.get("service")
        if posted_service:
            try:
                svc_obj = Service.objects.get(pk=posted_service, is_active=True)
                session["service_id"] = svc_obj.id
                request.session["iq2"] = session
                request.session.modified = True
            except Service.DoesNotExist:
                return redirect(f"{request.path}?dialog=1&step=1")
        else:
            return redirect(f"{request.path}?dialog=1&step=1")

    # ---- now safe to resolve service ----
    svc = get_object_or_404(Service, pk=session.get("service_id"), is_active=True)


    # ---------- STEP 2: dynamic details ----------
    if step == 2:
        schema = get_schema_for(svc)
        Step2Form = make_dynamic_form(schema)
        form = Step2Form(initial=session.get("step2", {}))
        if request.method == "POST":
            form = Step2Form(request.POST)
            if form.is_valid():
                session["step2"] = form.cleaned_data
                session["step"] = 3
                request.session["iq2"] = session
                return redirect(f"{request.path}?dialog=1&step=3")
        return _render_iq(request, {"step": 2, "form": form, "service": svc})

    # ---------- STEP 3: frequency ----------
    if step == 3:
        form = Step3FrequencyForm(initial=session.get("step3", {}))
        if request.method == "POST":
            form = Step3FrequencyForm(request.POST)
            if form.is_valid():
                session["step3"] = form.cleaned_data
                session["step"] = 4
                request.session["iq2"] = session
                return redirect(f"{request.path}?dialog=1&step=4")
        return _render_iq(request, {"step": 3, "form": form, "service": svc})

    # ---------- STEP 4: contact + create request ----------
    form = Step4ContactForm(initial=session.get("step4", {}))
    if request.method == "POST":
        form = Step4ContactForm(request.POST)
        if form.is_valid():
            session["step4"] = form.cleaned_data
            c = session["step4"]

            customer, created = Customer.objects.get_or_create(
                email=c.get("email") or None,
                defaults=dict(
                    full_name=c["full_name"],
                    phone=c.get("phone"),
                    address_line=c.get("address_line"),
                    suburb=c.get("suburb"),
                    state=c.get("state"),
                    postcode=c.get("postcode"),
                ),
            )
            if not created:
                for k in ("full_name", "phone", "address_line", "suburb", "state", "postcode"):
                    if c.get(k) is not None:
                        setattr(customer, k, c.get(k))
                customer.save()

            # Create request (NO price shown to user)
            # Create request (NO price shown to user)
            req = Request.objects.create(
                customer=customer,
                service=svc,
                status="new",
                # Step4ContactForm doesn't have date/time fields, so use safe defaults:
                preferred_date=timezone.localdate(),
                preferred_time=None,
                additional_details=(
                    "Instant Quote (modal) — "
                    f"step2: {session.get('step2', {})}, "
                    f"frequency: {session.get('step3', {})}. "
                    "Preferred date/time not provided in instant-quote modal."
                ),
            )
            Activity.objects.create(customer=customer, request=req, type="system",
                                    message="Instant Quote submitted via modal")

            # Notify client (if email) and admin
            if customer.email:
                send_mail(
                    subject=f"Thanks {customer.full_name} — we received your request",
                    message=(
                        f"Hi {customer.full_name},\n\n"
                        f"Thanks for requesting {svc.name}. Our team will confirm your quote shortly.\n"
                        f"Reference: #{req.id}\n\nB&T Bright Spotless Cleaning Services"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[customer.email],
                    fail_silently=True,
                )
            send_mail(
                subject=f"New Instant Quote: {svc.name} (#{req.id})",
                message=(
                    f"Customer: {customer.full_name} ({customer.email or 'no email'})\n"
                    f"Phone: {customer.phone or '—'}\n"
                    f"Service: {svc.name}\n"
                    f"Payload step2: {session.get('step2', {})}\n"
                    f"Frequency: {session.get('step3', {})}\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")],
                fail_silently=True,
            )

            # clear session and go to success page
            if "iq2" in request.session:
                del request.session["iq2"]
            return redirect("booking_success")

    return _render_iq(request, {"step": 4, "form": form, "service": svc})
