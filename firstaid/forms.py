from django import forms


class GuideSearchForm(forms.Form):
    q = forms.CharField(
        required=False, max_length=120, label="Search guides",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "CPR, bleeding, burns…"}),
    )
    page = forms.IntegerField(required=False, min_value=1, widget=forms.HiddenInput)

    def clean_q(self):
        return " ".join(self.cleaned_data["q"].split())
