from django import forms

from .models import Facility, Speciality


class FacilitySearchForm(forms.Form):
    """The HTML page and API deliberately accept the same search parameters."""

    q = forms.CharField(required=False, max_length=120, label="Name or address")
    facility_type = forms.ChoiceField(
        required=False, label="Facility type",
        choices=[("", "All facilities"), *Facility.Type.choices],
    )
    speciality = forms.ModelChoiceField(
        queryset=Speciality.objects.all(), to_field_name="slug", required=False,
        empty_label="All specialities",
    )
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
        self.fields["radius_km"].widget.attrs.update({"step": "any", "placeholder": "Any distance"})

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
        return data
