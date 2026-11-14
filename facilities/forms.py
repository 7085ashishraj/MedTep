from django import forms
from django.conf import settings

from .models import Facility, Speciality


class FacilitySearchForm(forms.Form):
    """The HTML page and API deliberately accept the same search parameters."""

    q = forms.CharField(required=False, max_length=120, label="Name or address")
    facility_type = forms.ChoiceField(
        required=False, label="Facility type",
        choices=[("", "All facilities"), *Facility.Type.choices],
    )
    speciality = forms.ChoiceField(required=False)
    open_24x7 = forms.BooleanField(required=False, label="24×7 only")
    latitude = forms.FloatField(required=False, min_value=-90, max_value=90)
    longitude = forms.FloatField(required=False, min_value=-180, max_value=180)
    radius_km = forms.FloatField(
        required=False, min_value=0.1, max_value=500, label="Within (km)",
        help_text="Optional, 0.1–500 km. Requires both coordinates.",
    )
    page = forms.IntegerField(required=False, min_value=1, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        specialities = {
            "cardiology": "Cardiology", "emergency": "Emergency care", "general": "General medicine",
            "gynaecology": "Gynaecology", "orthopaedics": "Orthopaedics", "paediatrics": "Paediatrics",
        }
        specialities.update(dict(Speciality.objects.values_list("slug", "name")))
        unique_labels = {label.casefold(): (slug, label) for slug, label in specialities.items()}
        self.fields["speciality"].choices = [("", "All specialities"), *sorted(unique_labels.values(), key=lambda pair: pair[1])]
        if settings.FACILITIES_LIVE_ENABLED:
            self.fields["radius_km"].max_value = 25
            self.fields["radius_km"].widget.attrs["max"] = 25
            self.fields["radius_km"].help_text = "Default 5 km. Search 0.1–25 km around your location."
            self.fields["radius_km"].widget.attrs["placeholder"] = "5 km"
        for name, field in self.fields.items():
            if name == "open_24x7":
                field.widget.attrs["class"] = "form-check-input"
            elif not field.widget.is_hidden:
                field.widget.attrs["class"] = (
                    "form-select" if isinstance(field.widget, forms.Select) else "form-control"
                )
        self.fields["q"].widget.attrs["placeholder"] = "Hospital, pharmacy or address"
        for name in ("latitude", "longitude"):
            self.fields[name].widget.attrs.update({"step": "any", "inputmode": "decimal"})
        self.fields["radius_km"].widget.attrs["step"] = "any"

    def clean_q(self):
        return " ".join(self.cleaned_data["q"].split())

    def clean(self):
        data = super().clean()
        # Do not add a misleading pair error when a field already failed validation.
        if "latitude" in self.errors or "longitude" in self.errors:
            return data
        latitude, longitude = data.get("latitude"), data.get("longitude")
        if (latitude is None) != (longitude is None):
            raise forms.ValidationError("Enter both latitude and longitude, or leave both blank.")
        if data.get("radius_km") is not None and latitude is None:
            raise forms.ValidationError("Add a location before filtering by distance.")
        if settings.FACILITIES_LIVE_ENABLED and (data.get("radius_km") or 0) > 25:
            self.add_error("radius_km", "Choose a radius up to 25 km for live searches.")
        return data
