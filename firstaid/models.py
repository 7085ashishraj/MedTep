from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from common.models import TimeStampedModel
from django.core.exceptions import ValidationError

from .validators import validate_https_source, validate_not_future


class FirstAidGuide(TimeStampedModel):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    summary = models.TextField()
    audience = models.CharField(max_length=100, default="Adults (18 years and over)")
    urgent_advice = models.TextField(blank=True)
    warnings = models.TextField(blank=True)
    source_url = models.URLField(blank=True, validators=[validate_https_source])
    supporting_source_url = models.URLField(blank=True, validators=[validate_https_source])
    source_checked_on = models.DateField(
        null=True, blank=True, validators=[validate_not_future],
        help_text="Date the linked sources were checked; not a clinical review.",
    )
    reviewed_on = models.DateField(
        null=True, blank=True, validators=[validate_not_future],
        help_text="Only enter a date if a qualified clinician actually reviewed this app's text.",
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["title", "pk"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.is_published:
            errors = {}
            if not self.source_url:
                errors["source_url"] = "A published guide needs an authoritative source link."
            if not self.source_checked_on:
                errors["source_checked_on"] = "Record when the source was actually checked."
            if errors:
                raise ValidationError(errors)


class FirstAidStep(models.Model):
    guide = models.ForeignKey(
        FirstAidGuide, on_delete=models.CASCADE, related_name="steps",
    )
    position = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    heading = models.CharField(max_length=120, blank=True)
    instruction = models.TextField()

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["guide", "position"], name="unique_position_per_guide",
            ),
            models.CheckConstraint(
                condition=models.Q(position__gte=1), name="firstaid_positive_position",
            ),
        ]

    def __str__(self):
        return f"{self.guide.title}: step {self.position}"


class EmergencyHelpline(TimeStampedModel):
    name = models.CharField(max_length=100)
    number = models.CharField(
        max_length=16,
        validators=[RegexValidator(r"\A\+?[0-9]{2,15}\Z", "Enter 2 to 15 digits; optional +.")],
    )
    region = models.CharField(max_length=100, help_text="Country, state, or service area.")
    description = models.TextField(blank=True)
    is_nationwide = models.BooleanField(default=False)
    source_url = models.URLField(blank=True, validators=[validate_https_source])
    verified_on = models.DateField(
        null=True, blank=True, validators=[validate_not_future],
        help_text="Date the official source was checked; this does not record a test call.",
    )
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["region", "name", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["number", "region"], name="unique_helpline_number_per_region",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.number})"

    def clean(self):
        super().clean()
        if self.is_active and (not self.source_url or not self.verified_on):
            raise ValidationError("An active helpline needs an official source and its check date.")
