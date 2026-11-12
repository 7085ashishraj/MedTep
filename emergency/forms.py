import uuid

from django import forms
from django.db.models import Q

from facilities.models import Facility

from .ambulance_services import allowed_statuses
from .models import AmbulanceRequest


class EmergencyRequestForm(forms.Form):
    request_id = forms.UUIDField(widget=forms.HiddenInput, initial=uuid.uuid4)
    latitude = forms.DecimalField(max_digits=8, decimal_places=6, min_value=-90, max_value=90)
    longitude = forms.DecimalField(max_digits=9, decimal_places=6, min_value=-180, max_value=180)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("latitude", "longitude"):
            self.fields[name].widget.attrs.update({
                "class": "form-control", "step": "any", "inputmode": "decimal",
            })


class ReferenceFacilityField(forms.ModelChoiceField):
    def label_from_instance(self, facility):
        return facility.name + (" · FAKE sample" if facility.is_demo else "") + (" · inactive" if not facility.is_active else "")


class AmbulanceOperatorForm(forms.Form):
    expected_version = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    status = forms.ChoiceField(choices=AmbulanceRequest.Status.choices)
    facility = ReferenceFacilityField(
        queryset=Facility.objects.none(), required=False, label="Reference facility",
        help_text="A directory reference only; selecting it does not contact a provider.",
    )
    operator_notes = forms.CharField(
        required=False, max_length=2000, label="Internal operator notes",
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Visible only to authorised operators. Do not enter medical-profile details.",
    )

    def __init__(self, *args, ambulance, **kwargs):
        kwargs.setdefault("initial", {
            "expected_version": ambulance.version, "status": ambulance.status,
            "facility": ambulance.facility_id, "operator_notes": ambulance.operator_notes,
        })
        super().__init__(*args, **kwargs)
        choices = allowed_statuses(ambulance.status)
        self.fields["status"].choices = [(value, label) for value, label in AmbulanceRequest.Status.choices if value in choices]
        eligible = Q(is_active=True, facility_type__in=[Facility.Type.HOSPITAL, Facility.Type.CLINIC])
        self.fields["facility"].queryset = Facility.objects.filter(eligible | Q(pk=ambulance.facility_id))
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"


class AmbulanceDashboardForm(forms.Form):
    status = forms.ChoiceField(
        required=False,
        choices=[("open", "Open requests"), ("all", "All requests"), *AmbulanceRequest.Status.choices],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    page = forms.IntegerField(required=False, min_value=1, widget=forms.HiddenInput)
