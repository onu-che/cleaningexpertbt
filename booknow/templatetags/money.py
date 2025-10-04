# booknow/templatetags/money.py
from django import template
register = template.Library()

@register.filter
def aud_cents(cents):
    """Format integer cents -> $X.YY"""
    try:
        v = int(cents)
        return f"${v/100:,.2f}"
    except Exception:
        return ""
