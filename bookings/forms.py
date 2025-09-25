from django import forms
from crm.models import Service
from django.utils import timezone

class BookingForm(forms.Form):
    # fields (unchanged) ...
    full_name = forms.CharField(max_length=255)
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=20, required=False)
    address_line = forms.CharField(max_length=255, required=False)
    suburb = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=False)
    postcode = forms.CharField(max_length=10, required=False)
    service = forms.ModelChoiceField(queryset=Service.objects.none())  # set in __init__
    preferred_date = forms.DateField(widget=forms.SelectDateWidget)
    preferred_time = forms.TimeField(required=False, widget=forms.TimeInput(format='%H:%M'))
    additional_details = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        initial_service = kwargs.pop("initial_service", None)
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)
        if initial_service:
            self.fields["service"].initial = initial_service

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("email") and not cleaned.get("phone"):
            raise forms.ValidationError("Please provide at least an email or a phone number.")
        d = cleaned.get("preferred_date")
        if d and d < timezone.now().date():
            raise forms.ValidationError("Preferred date cannot be in the past.")
        return cleaned

# ==== Instant Quote wizard forms ====

# --- Step 1 (cards) ---
class Step1ServiceForm(forms.Form):
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        widget=forms.HiddenInput  # selected via card click (JS sets value)
    )

# --- Step 3 ---
class Step3FrequencyForm(forms.Form):
    FREQUENCY_CHOICES = [
        ("weekly", "Every Week"),
        ("fortnightly", "Every 2 Weeks"),
        ("monthly", "Every 4 Weeks"),
        ("one_off", "1 Time Service"),
    ]
    frequency = forms.ChoiceField(choices=FREQUENCY_CHOICES, initial="one_off")

# --- Step 4 ---
class Step4ContactForm(forms.Form):
    full_name = forms.CharField(max_length=255, label="Full name")
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=20, required=False)
    address_line = forms.CharField(max_length=255, required=False, label="Street address")
    suburb = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100, required=False)
    postcode = forms.CharField(max_length=10, required=False)

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("email") and not cleaned.get("phone"):
            raise forms.ValidationError("Provide at least an email or a phone number.")
        return cleaned
