from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone
from .models import Request, Service, Customer

@staff_member_required
def admin_dashboard(request):
    today = timezone.now().date()
    week_start = today - timezone.timedelta(days=today.weekday())  # Monday

    kpi_new_this_week = Request.objects.filter(created_at__date__gte=week_start).count()
    kpi_scheduled = Request.objects.filter(status="scheduled").count()
    kpi_completed = Request.objects.filter(status="completed").count()
    revenue_ytd = (
        Request.objects.filter(status="completed", created_at__year=today.year)
        .aggregate(total=Sum("price_quote"))
        .get("total") or 0
    )

    top_services = (
        Request.objects.values("service__name")
        .annotate(n=Count("id"))
        .order_by("-n")[:5]
    )

    return render(request, "crm/admin_dashboard.html", {
        "kpi_new_this_week": kpi_new_this_week,
        "kpi_scheduled": kpi_scheduled,
        "kpi_completed": kpi_completed,
        "revenue_ytd": revenue_ytd,
        "top_services": top_services,
        "today": today,
        "week_start": week_start,
    })
