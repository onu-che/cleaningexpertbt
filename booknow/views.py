# booknow/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import ServiceCategory, Service, Booking 
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime, date
from zoneinfo import ZoneInfo
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import logging
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives



SESSION_KEY = "booknow"


logger = logging.getLogger(__name__)

def safe_send_mail(subject, message, to_list):
    try:
        send_mail(
            subject, message,
            settings.DEFAULT_FROM_EMAIL,
            to_list,
            fail_silently=False
        )
        return True
    except Exception as e:
        logger.exception("Email send failed: %s", e)
        return False
# --- Live Price Estimator Rules (all in cents) ---
ESTIMATOR_RULES = {
    "gym-cleaning": {
        "base": 15000,   # $150 base
        "rates": {"area_sqm": 150, "equipment_count": 300, "showers": 500},
        "extras": {}
    },
    "medical-cleaning": {
        "base": 18000,
        "rates": {"consult_rooms": 1200, "treatment_rooms": 1500, "area_sqm": 150},
        "extras": {}
    },
    "pub-cleaning": {
        "base": 14000,
        "rates": {"area_sqm": 140, "bars": 1000},
        "extras": {}
    },
    "strata-cleaning": {
        "base": 16000,
        "rates": {"common_areas": 1200, "levels": 2000},
        "extras": {}
    },
    "post-construction": {
        "base": 20000,
        "rates": {"area_sqm": 200, "rooms": 1200},
        "extras": {}
    },
    "residential-cleaning": {
        "base": 11000,
        "rates": {"bedrooms": 1500, "bathrooms": 2500, "area_sqm": 100},
        "extras": {"oven": 3000, "windows": 3000}
    },
    "end-of-lease-cleaning": {
        "base": 18000,
        "rates": {"bedrooms": 2000, "bathrooms": 3000, "area_sqm": 150},
        "extras": {"oven": 3000, "windows": 3000, "carpet": 2500}
    },
    "laundry-fold-ironing": {
        "base": 8000,
        "rates": {"laundry_bags": 3000, "iron_items": 200},
        "extras": {}
    },
    "child-care-centre": {
        "base": 17000,
        "rates": {"rooms": 1500, "area_sqm": 150},
        "extras": {}
    },
    # default if slug not matched
    "_default": {"base": 10000, "rates": {}, "extras": {}}
}

def _estimator_for(service_slug: str):
    """Return estimator config for given service slug."""
    return ESTIMATOR_RULES.get(service_slug, ESTIMATOR_RULES["_default"])


# ---- Dynamic details schemas (data-driven Details step) ----
# Field spec:
#  - name: machine key saved into Booking.details
#  - label: user-facing text
#  - type: "number" | "text" | "select" | "textarea"
#  - min: (optional) numeric min
#  - options: (for "select") list of [value, label]
SERVICE_DETAIL_SCHEMAS = {
    "gym-cleaning": [
        {"name": "area_sqm",         "label": "Approx. area (sqm)",         "type": "number",  "min": 0},
        {"name": "equipment_count",  "label": "Equipment count",            "type": "number",  "min": 0},
        {"name": "showers",          "label": "Showers / change rooms",     "type": "number",  "min": 0},
        {"name": "foot_traffic",     "label": "Typical foot traffic",       "type": "select",  "options": [["low","Low"],["medium","Medium"],["high","High"]]},
        {"name": "opening_hours",    "label": "Preferred cleaning window",  "type": "text"},
        {"name": "notes",            "label": "Other requirements",         "type": "textarea"},
    ],
    "medical-cleaning": [
        {"name": "consult_rooms",    "label": "Consult rooms",              "type": "number", "min": 0},
        {"name": "treatment_rooms",  "label": "Treatment rooms",            "type": "number", "min": 0},
        {"name": "reception_sqm",    "label": "Reception area (sqm)",       "type": "number", "min": 0},
        {"name": "compliance",       "label": "Compliance needs (e.g., infection control)", "type": "text"},
        {"name": "sharps_bins",      "label": "Sharps bins present?",       "type": "select", "options": [["no","No"],["yes","Yes"]]},
        {"name": "notes",            "label": "Other requirements",         "type": "textarea"},
    ],
    "pub-cleaning": [
        {"name": "trading_hours",    "label": "Trading hours / clean window","type": "text"},
        {"name": "bar_count",        "label": "Bar counters",               "type": "number", "min": 0},
        {"name": "dining_seats",     "label": "Dining seats (approx.)",     "type": "number", "min": 0},
        {"name": "kitchen_clean",    "label": "Include kitchen clean?",     "type": "select", "options": [["no","No"],["yes","Yes"]]},
        {"name": "outdoor_sqm",      "label": "Outdoor area (sqm)",         "type": "number", "min": 0},
        {"name": "spill_level",      "label": "Sticky spill level",         "type": "select", "options": [["low","Low"],["medium","Medium"],["high","High"]]},
        {"name": "notes",            "label": "Other requirements",         "type": "textarea"},
    ],
    "strata-cleaning": [
        {"name": "building_floors",  "label": "Building floors",            "type": "number", "min": 1},
        {"name": "lobbies",          "label": "Lobbies / foyers",           "type": "number", "min": 0},
        {"name": "lift_count",       "label": "Lifts",                      "type": "number", "min": 0},
        {"name": "bin_rooms",        "label": "Bin rooms",                  "type": "number", "min": 0},
        {"name": "carpark_levels",   "label": "Car park levels",            "type": "number", "min": 0},
        {"name": "common_area_sqm",  "label": "Common areas (sqm)",         "type": "number", "min": 0},
        {"name": "window_cleaning",  "label": "Include window cleaning?",   "type": "select", "options": [["no","No"],["yes","Yes"]]},
        {"name": "notes",            "label": "Other requirements",         "type": "textarea"},
    ],
    "end-of-lease-cleaning": [
        {"name": "bedrooms",         "label": "Bedrooms",                   "type": "number", "min": 0},
        {"name": "bathrooms",        "label": "Bathrooms",                  "type": "number", "min": 0},
        {"name": "storeys",          "label": "Storey / floor level",       "type": "number", "min": 1},
        {"name": "balcony_count",    "label": "Balconies",                  "type": "number", "min": 0},
        {"name": "oven_clean",       "label": "Include oven clean?",        "type": "select", "options": [["no","No"],["yes","Yes"]]},
        {"name": "blinds_clean",     "label": "Include blinds clean?",      "type": "select", "options": [["no","No"],["yes","Yes"]]},
        {"name": "carpet_steam",     "label": "Carpet steam required?",     "type": "select", "options": [["no","No"],["yes","Yes"]]},
        {"name": "notes",            "label": "Other requirements",         "type": "textarea"},
    ],
    "post-construction": [
        {"name": "area_sqm",         "label": "Approx. area (sqm)",         "type": "number", "min": 0},
        {"name": "rooms",            "label": "Rooms (total)",              "type": "number", "min": 0},
        {"name": "debris_level",     "label": "Debris / dust level",        "type": "select", "options": [["light","Light"],["medium","Medium"],["heavy","Heavy"]]},
        {"name": "paint_splatter",   "label": "Paint splatter present?",    "type": "select", "options": [["no","No"],["yes","Yes"]]},
        {"name": "site_power",       "label": "Site power available?",      "type": "select", "options": [["yes","Yes"],["no","No"]]},
        {"name": "notes",            "label": "Other requirements",         "type": "textarea"},
    ],
    "residential-cleaning": [
        {"name": "bedrooms",         "label": "Bedrooms",                   "type": "number", "min": 0},
        {"name": "bathrooms",        "label": "Bathrooms",                  "type": "number", "min": 0},
        {"name": "storeys",          "label": "Storey / floor level",       "type": "number", "min": 1},
        {"name": "pets",             "label": "Pets at home",               "type": "select", "options": [["none","None"],["dog","Dog"],["cat","Cat"],["other","Other"]]},
        {"name": "priority_areas",   "label": "Priority areas",             "type": "text"},
        {"name": "notes",            "label": "Other requirements",         "type": "textarea"},
    ],
    "laundry-fold-ironing": [
        {"name": "load_count",       "label": "Laundry loads (approx.)",    "type": "number", "min": 0},
        {"name": "include_ironing",  "label": "Include ironing?",           "type": "select", "options": [["no","No"],["yes","Yes"]]},
        {"name": "hang_dry",         "label": "Hang dry required?",         "type": "select", "options": [["no","No"],["yes","Yes"]]},
        {"name": "detergent_provided","label":"Detergent provided?",        "type": "select", "options": [["yes","Yes"],["no","No"]]},
        {"name": "pickup_delivery",  "label": "Pickup/Delivery needed?",    "type": "select", "options": [["no","No"],["pickup","Pickup"],["delivery","Delivery"],["both","Both"]]},
        {"name": "notes",            "label": "Other requirements",         "type": "textarea"},
    ],
    "office-cleaning": [
        {"name": "area_sqm",         "label": "Approx. area (sqm)",         "type": "number", "min": 0},
        {"name": "desk_count",       "label": "Desks",                      "type": "number", "min": 0},
        {"name": "meeting_rooms",    "label": "Meeting rooms",              "type": "number", "min": 0},
        {"name": "kitchenettes",     "label": "Kitchenettes",               "type": "number", "min": 0},
        {"name": "bathrooms",        "label": "Bathrooms",                  "type": "number", "min": 0},
        {"name": "after_hours",      "label": "After-hours access needed?", "type": "select", "options": [["no","No"],["yes","Yes"]]},
        {"name": "security_clearance","label":"Security clearance required?","type": "select", "options": [["no","No"],["yes","Yes"]]},
        {"name": "notes",            "label": "Other requirements",         "type": "textarea"},
    ],
    "child-care-centre": [
        {"name": "rooms",            "label": "Rooms (total)",              "type": "number", "min": 0},
        {"name": "bathrooms",        "label": "Bathrooms",                  "type": "number", "min": 0},
        {"name": "change_stations",  "label": "Nappy change stations",      "type": "number", "min": 0},
        {"name": "playground_sqm",   "label": "Playground area (sqm)",      "type": "number", "min": 0},
        {"name": "sanitisation_focus","label":"Sanitisation focus",         "type": "select", "options": [["toys","Toys"],["sleep_mats","Sleep mats"],["kitchen","Kitchen"],["all","All"]]},
        {"name": "compliance",       "label": "Compliance notes (e.g., ACECQA)", "type": "text"},
        {"name": "notes",            "label": "Other requirements",         "type": "textarea"},
    ],
}

# ---- Optional aliases (if Admin uses variant slugs) ----
SERVICE_DETAIL_SCHEMAS["end-of-lease"]      = SERVICE_DETAIL_SCHEMAS["end-of-lease-cleaning"]
SERVICE_DETAIL_SCHEMAS["new-build"]         = SERVICE_DETAIL_SCHEMAS["post-construction"]
SERVICE_DETAIL_SCHEMAS["house-cleaning"]    = SERVICE_DETAIL_SCHEMAS["residential-cleaning"]
SERVICE_DETAIL_SCHEMAS["laundry-services"]  = SERVICE_DETAIL_SCHEMAS["laundry-fold-ironing"]
SERVICE_DETAIL_SCHEMAS["child-care"]        = SERVICE_DETAIL_SCHEMAS["child-care-centre"]

DEFAULT_DETAILS_SCHEMA = [
    {"name": "notes", "label": "Other requirements", "type": "textarea"},
]

def _details_schema_for_slug(slug: str):
    return SERVICE_DETAIL_SCHEMAS.get(slug, DEFAULT_DETAILS_SCHEMA)



def _get_state(request):
    return request.session.get(SESSION_KEY, {})

def _save_state(request, data: dict):
    request.session[SESSION_KEY] = data
    request.session.modified = True

def _clear_state(request):
    if SESSION_KEY in request.session:
        del request.session[SESSION_KEY]


def _aud(cents: int | None) -> str:
    try:
        return f"${int(cents)/100:,.2f}"
    except Exception:
        return ""


# Small helper to pick the details-section key from the slug
def _service_key_from_slug(slug: str) -> str:
    slug = (slug or "").replace("-", "").lower()
    # Map known slugs to our template section keys
    if "gym" in slug: return "gym"
    if "medical" in slug: return "medical"
    if "endoflease" in slug: return "endoflease"
    if "newbuild" in slug or "construction" in slug: return "newbuild"
    if "house" in slug or "residential" in slug: return "house"
    return ""

# 1) Service Selection
def service_select(request):
    state = _get_state(request)

    if request.method == "POST":
        category_slug = request.POST.get("category_slug", "").strip()
        service_id = request.POST.get("service_id", "").strip()

        if not service_id:
            # fall back with an error; reload with DB data
            categories = ServiceCategory.objects.order_by("sort_order", "name").all()
            services = Service.objects.select_related("category").order_by("category__sort_order", "name")
            return render(request, "booknow/service_select.html", {
                "state": state, "current_step": "service",
                "categories": categories, "services": services,
                "error": "Please choose a service.",
            })

        svc = get_object_or_404(Service, pk=service_id)
        cat_slug = category_slug or (svc.category.slug if svc.category_id else "")

        state.update({
            "service_category": cat_slug,
            "service_id": str(svc.pk),
            "service_slug": svc.slug,
            "service_key": _service_key_from_slug(svc.slug),
            "service_name": svc.name,
        })
        _save_state(request, state)
        return redirect("booknow_details")
    

    # GET → load from DB
    categories = ServiceCategory.objects.order_by("sort_order", "name").all()
    services = Service.objects.select_related("category").order_by("category__sort_order", "name")
    return render(request, "booknow/service_select.html", {
        "state": state, "current_step": "service",
        "categories": categories, "services": services,
    })

# 2) Details (tiny tweak to ensure service_key is available)
def details(request):
    state = _get_state(request)
    if not state.get("service_id"):
        return redirect("booknow_service")

    service = get_object_or_404(Service, pk=state["service_id"])
    schema = _details_schema_for_slug(state.get("service_slug", ""))

    if request.method == "POST":
        details_payload = {}
        for k, v in request.POST.items():
            if k in {"csrfmiddlewaretoken", "price_estimate"}:
                continue
            details_payload[k] = (v or "").strip()

        # persist details
        state["details"] = details_payload

        # persist estimate (cents) if present
        pe = request.POST.get("price_estimate")
        if pe and pe.isdigit():
            state["price_estimate"] = int(pe)

        _save_state(request, state)
        return redirect("booknow_schedule")

    ctx = {
        "schema": schema,
        "state": state,
        "service": service,
        "current_step": "details",
        "estimator_enabled": getattr(settings, "ENABLE_ESTIMATOR", False),
        "service_slug": service.slug,
        "estimator_rules": _estimator_for(service.slug),
    }
    return render(request, "booknow/details.html", ctx)


# 3) Schedule: date, time, frequency
def schedule(request):
    state = _get_state(request)
    service_id = state.get("service_id")
    if not service_id:
        return redirect("booknow_service")

    service = get_object_or_404(Service, pk=service_id)

    if request.method == "POST":
        # read from POST into locals for validation
        preferred_date = request.POST.get("preferred_date", "").strip()
        preferred_time = request.POST.get("preferred_time", "").strip()
        frequency      = request.POST.get("frequency", "one_time").strip()
        access_window  = request.POST.get("access_window", "").strip()  # optional if you add this field

        # Validate
        error = None
        try:
            d = _parse_date(preferred_date)
            if d < _today_sydney():
                error = "Please select today or a future date."
        except Exception:
            error = "Please enter a valid date (YYYY-MM-DD)."

        if not error:
            try:
                _ = _parse_time(preferred_time)
            except Exception:
                error = "Please enter a valid time."

        if error:
            ctx = {
                "state": state,
                "service": service,
                "current_step": "schedule",
                "estimator_enabled": getattr(settings, "ENABLE_ESTIMATOR", False),
                "service_slug": service.slug,
                "estimator_rules": _estimator_for(service.slug),
                "error": error,
                "sticky": {
                    "preferred_date": preferred_date,
                    "preferred_time": preferred_time,
                    "frequency": frequency,
                    "access_window": access_window,
                },
            }
            return render(request, "booknow/schedule.html", ctx)

        # Save validated schedule + estimate into session
        state.update({
            "preferred_date": preferred_date,
            "preferred_time": preferred_time,
            "frequency": frequency or "one_time",
            "access_window": access_window,
        })

        pe = request.POST.get("price_estimate")
        if pe and pe.isdigit():
            state["price_estimate"] = int(pe)

        _save_state(request, state)
        return redirect("booknow_contact")

    # GET — build ctx
    ctx = {
        "state": state,
        "service": service,
        "current_step": "schedule",
        "estimator_enabled": getattr(settings, "ENABLE_ESTIMATOR", False),
        "service_slug": service.slug,
        "estimator_rules": _estimator_for(service.slug),
        "sticky": {
            "preferred_date": state.get("preferred_date", ""),
            "preferred_time": state.get("preferred_time", ""),
            "frequency": state.get("frequency", "one_time"),
            "access_window": state.get("access_window", ""),
        },
    }
    return render(request, "booknow/schedule.html", ctx)



# 4) Contact: name, email, phone, address
def contact(request):
    state = _get_state(request)
    if not state.get("service_id"):
        return redirect("booknow_service")

    ctx = {"state": state, "current_step": "contact"}
    if request.method == "POST":
        contact = {
            "name": (request.POST.get("name") or "").strip(),
            "email": (request.POST.get("email") or "").strip(),
            "phone": (request.POST.get("phone") or "").strip(),
            "address_line": (request.POST.get("address_line") or "").strip(),
            "suburb": (request.POST.get("suburb") or "").strip(),
            "state": (request.POST.get("state") or "").strip().upper(),
            "postcode": (request.POST.get("postcode") or "").strip(),
            "parking_notes": (request.POST.get("parking_notes") or "").strip(),
        }

        # Validate
        error = None
        if not contact["name"] or not contact["email"] or not contact["phone"]:
            error = "Name, email, and phone are required."
        else:
            try:
                validate_email(contact["email"])
            except ValidationError:
                error = "Please enter a valid email address."
            if not error and contact["state"] not in AU_STATES:
                error = "Please select a valid Australian state."
            if not error and (len(contact["postcode"]) != 4 or not contact["postcode"].isdigit()):
                error = "Postcode must be 4 digits (e.g., 2000)."
            if not error and (not contact["address_line"] or not contact["suburb"]):
                error = "Please complete the service address."

        if error:
            ctx["error"] = error
            ctx["sticky"] = contact
            return render(request, "booknow/contact.html", ctx)

        state["contact"] = contact
        _save_state(request, state)
        return redirect("booknow_review")

    # GET — sticky from session
    ctx["sticky"] = state.get("contact", {})
    return render(request, "booknow/contact.html", ctx)



AU_STATES = {"NSW","VIC","QLD","SA","WA","TAS","ACT","NT"}

def _today_sydney() -> date:
    tz = ZoneInfo("Australia/Sydney")
    now = datetime.now(tz)
    return now.date()

def _parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

def _parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M").time()


def _make_admin_email_subject(b: Booking):
    return f"[New Booking] {b.service.name} · {b.name} · {b.suburb}"




def _make_admin_email_body(b: Booking):
    return (
        "NEW BOOKING\n"
        f"Service: {b.service.name}\n"
        f"Customer: {b.name} <{b.email}>\n"
        f"Address: {b.address_line}, {b.suburb} {b.state} {b.postcode}\n"
        f"Preferred: {b.preferred_date} {b.preferred_time}\n"
        f"Access window: {b.access_window or '-'}\n"
        f"Parking/access: {b.parking_notes or '-'}\n"
        f"\nStatus: {b.get_status_display()}\n"
        f"Created: {b.created_at:%Y-%m-%d %H:%M}\n"
    )

def _make_customer_email_subject(b: Booking):
    return f"Booking received – {b.service.name}"

def _make_customer_email_body(b: Booking):
    booking_ref = getattr(b, "id", None)
    return (
        f"Service: {b.service.name}\n"
        f"Date & time: {b.preferred_date} {b.preferred_time}\n"
        f"Access window: {b.access_window or '-'}\n"
        f"Parking/access: {b.parking_notes or '-'}\n\n"
        "We'll confirm availability shortly. If anything changes, just reply to this email.\n\n"
        f"Booking reference: #{booking_ref or 'N/A'}\n\n"
        "— Cleaning Expert BT\n"
        "cleaningexpertbt.com.au\n"
    )

def _send_booking_emails(ctx: dict):
    """Send admin + customer emails for a new booking, including estimate."""
    booking = ctx["booking"]
    estimate = ctx["estimate_display"]

    from_addr = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")

    # --- Admin email ---
    subject_admin = f"[New Booking] {booking.service.name} on {booking.preferred_date} — {estimate or ''}".strip()
    body_admin_txt = render_to_string("booknow/emails/booking_admin.txt", ctx)
    body_admin_html = render_to_string("booknow/emails/booking_admin.html", ctx)
    to_admin = [getattr(settings, "BOOKING_ADMIN_EMAIL", from_addr)]
    msg = EmailMultiAlternatives(subject_admin, body_admin_txt, from_addr, to_admin)
    msg.attach_alternative(body_admin_html, "text/html")
    msg.send(fail_silently=False)

    # --- Customer email ---
    if booking.email:
        subject_cust = f"Booking received — {booking.service.name} ({estimate or 'No estimate'})"
        body_cust_txt = render_to_string("booknow/emails/booking_customer.txt", ctx)
        body_cust_html = render_to_string("booknow/emails/booking_customer.html", ctx)
        msg2 = EmailMultiAlternatives(subject_cust, body_cust_txt, from_addr, [booking.email])
        msg2.attach_alternative(body_cust_html, "text/html")
        msg2.send(fail_silently=False)


def _create_booking_from_session(state):
    svc = Service.objects.get(pk=state["service_id"])
    contact = state.get("contact", {})

    # Parse date/time safely (you already validated earlier)
    pd = _parse_date(state["preferred_date"])
    pt = _parse_time(state["preferred_time"])

    b = Booking.objects.create(
        service=svc,
        name=contact.get("name",""),
        email=contact.get("email",""),
        phone=contact.get("phone",""),
        address_line=contact.get("address_line",""),
        suburb=contact.get("suburb",""),
        state=contact.get("state",""),
        postcode=contact.get("postcode",""),
        details=state.get("details", {}),
        preferred_date=pd,
        preferred_time=pt,
        frequency=state.get("frequency","one_time"),
        status=Booking.ST_NEW,
        price_estimate=state.get("price_estimate"),   # <-- save cents
    )
    return b






# 5) Review: display summary; on POST, go to thank-you (DB save next step)
def review(request):
    state = _get_state(request)
    if not state.get("service_id"):
        return redirect("booknow_service")

    if request.method == "POST":
        # Basic completeness check
        required_keys = ["service_id","preferred_date","preferred_time","frequency","contact"]
        if not all(k in state and state[k] for k in required_keys):
            return redirect("booknow_contact")

        # 1) Create booking in DB
        booking = _create_booking_from_session(state)

        # After: booking = _create_booking_from_session(state)
        ctx = {
            "booking": booking,
            "estimate_display": _aud(booking.price_estimate) if booking.price_estimate else "—",
        }

        _send_booking_emails(ctx)  # (create this helper below)


        # 2) Send emails (SMTP in prod, console in dev) was removed

# ===============================================================
        # 3) Clear session
        _clear_state(request)

        # 4) Redirect
        return redirect("booknow_thank_you")

    # GET — include service + estimator flag so template can show the saved estimate
    service = get_object_or_404(Service, pk=state["service_id"])
    ctx = {
        "state": state,
        "service": service,
        "current_step": "review",
        "estimator_enabled": getattr(settings, "ENABLE_ESTIMATOR", False),
    }
    return render(request, "booknow/review.html", ctx)

def thank_you(request):
    # state cleared after submit; just render a friendly message
    return render(request, "booknow/thank_you.html", {})






# =========================================

