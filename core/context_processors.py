from django.conf import settings

def flags(_request):
    return {
        "ENABLE_ESTIMATOR": getattr(settings, "ENABLE_ESTIMATOR", False),
        "ENABLE_STRIPE": getattr(settings, "ENABLE_STRIPE", False),
    }
