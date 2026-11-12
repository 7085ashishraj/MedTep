from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import EmergencyHelpline, FirstAidGuide, FirstAidStep


class GuideStepsFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        kept = [form for form in self.forms if form.cleaned_data and not form.cleaned_data.get("DELETE")
                and form.cleaned_data.get("instruction")]
        if self.instance.is_published and not kept:
            raise ValidationError("A published guide must have at least one instruction step.")
        positions = sorted(form.cleaned_data["position"] for form in kept)
        if positions and positions != list(range(1, len(positions) + 1)):
            raise ValidationError("Number steps consecutively from 1, without gaps.")


class FirstAidStepInline(admin.StackedInline):
    model = FirstAidStep
    formset = GuideStepsFormSet
    extra = 1
    fields = ["position", "heading", "instruction"]


@admin.register(FirstAidGuide)
class FirstAidGuideAdmin(admin.ModelAdmin):
    list_display = ["title", "audience", "is_published", "source_checked_on", "reviewed_on"]
    list_filter = ["is_published", "source_checked_on"]
    search_fields = ["title", "summary", "slug"]
    prepopulated_fields = {"slug": ["title"]}
    readonly_fields = ["created_at", "updated_at"]
    inlines = [FirstAidStepInline]
    fieldsets = [
        ("Guide", {"fields": ["title", "slug", "audience", "summary", "urgent_advice", "warnings"]}),
        ("Sources and publication", {"fields": ["source_url", "supporting_source_url", "source_checked_on", "reviewed_on", "is_published"],
         "description": "A source check is not a clinical review. Published summaries need current authoritative sources. Only record a clinical review if it actually took place."}),
        ("Record", {"fields": ["created_at", "updated_at"]}),
    ]


@admin.register(EmergencyHelpline)
class EmergencyHelplineAdmin(admin.ModelAdmin):
    list_display = ["name", "number", "region", "is_nationwide", "is_active", "verified_on"]
    list_filter = ["is_nationwide", "is_active"]
    search_fields = ["name", "number", "region"]
    readonly_fields = ["created_at", "updated_at"]
    fields = ["name", "number", "region", "description", "is_nationwide", "source_url", "verified_on", "is_active", "created_at", "updated_at"]
