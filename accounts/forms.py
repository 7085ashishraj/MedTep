import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from common.validators import phone_validator

from .models import EmergencyContact, MedicalProfile, User


class BootstrapFormMixin:
    """Share widget styling without repeating it in every form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                css_class = "form-select"
            else:
                css_class = "form-control"
            field.widget.attrs["class"] = css_class


class RegistrationForm(BootstrapFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=150, label="First name")
    last_name = forms.CharField(max_length=150, required=False, label="Last name")
    email = forms.EmailField(
        required=False,
        help_text="Optional. Login uses your username. Email is not verified in this demo.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, autocomplete in {
            "first_name": "given-name", "last_name": "family-name",
            "username": "username", "email": "email",
            "password1": "new-password", "password2": "new-password",
        }.items():
            self.fields[name].widget.attrs["autocomplete"] = autocomplete
        self.fields["username"].widget.attrs["autocapitalize"] = "none"


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "autocomplete": "username", "autocapitalize": "none",
        })
        self.fields["password"].widget.attrs["autocomplete"] = "current-password"


class MedicalProfileForm(BootstrapFormMixin, forms.ModelForm):
    allergies = forms.CharField(
        required=False, max_length=2000,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Record known allergies in your own words. Blank means not recorded.",
    )
    medical_conditions = forms.CharField(
        required=False, max_length=2000,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Include details you want to keep in your profile. Up to 2,000 characters.",
    )

    class Meta:
        model = MedicalProfile
        fields = ("blood_group", "allergies", "medical_conditions")
        help_texts = {"blood_group": "Choose Unknown if you do not know your blood group."}


class EmergencyContactForm(BootstrapFormMixin, forms.ModelForm):
    phone = forms.CharField(
        max_length=32,
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
        help_text="7–15 digits with an optional country prefix (+). Spaces, hyphens and brackets are accepted.",
    )

    class Meta:
        model = EmergencyContact
        fields = ("name", "relationship", "phone", "is_primary")
        labels = {"is_primary": "Make this my primary emergency contact"}
        help_texts = {"is_primary": "This replaces your current primary contact, if you have one."}

    def __init__(self, *args, profile, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.profile = profile
        self.fields["name"].widget.attrs["autocomplete"] = "name"

    def clean_phone(self):
        phone = re.sub(r"[\s()\-]", "", self.cleaned_data["phone"])
        phone_validator(phone)
        return phone
