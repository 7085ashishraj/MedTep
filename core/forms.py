from django import forms


class CareSearchForm(forms.Form):
    """A small entry form; the facilities app validates submitted searches."""

    q = forms.CharField(
        label="Facility name or address",
        required=False,
        max_length=120,
        widget=forms.TextInput(attrs={
            "id": "care-query",
            "class": "form-control",
            "placeholder": "Hospital, pharmacy or address",
            "autocomplete": "off",
            "aria-describedby": "search-hint",
        }),
    )

    def clean_q(self):
        return " ".join(self.cleaned_data["q"].split())
