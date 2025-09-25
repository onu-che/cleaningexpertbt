from django import forms

SUBJECT_CHOICES = [
    ("General", "General"),
    ("Quote", "Quote"),
    ("Partnership", "Partnership"),
    ("Other", "Other"),
]

class ContactForm(forms.Form):
    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False)
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES)
    message = forms.CharField(widget=forms.Textarea)
    # Honeypot (must stay empty)
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Bot detected.")
        return ""
