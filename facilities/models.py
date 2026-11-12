from django.db import models

from common.models import TimeStampedModel
from common.validators import latitude_validators, longitude_validators, phone_validator


class Speciality(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "specialities"

    def __str__(self):
        return self.name


class Facility(TimeStampedModel):
    class Type(models.TextChoices):
        HOSPITAL = "hospital", "Hospital"
        CLINIC = "clinic", "Clinic"
        PHARMACY = "pharmacy", "Pharmacy"
        BLOOD_BANK = "blood_bank", "Blood bank"

    name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=20, choices=Type.choices)
    specialities = models.ManyToManyField(
        Speciality, blank=True, related_name="facilities",
    )
    address = models.TextField()
    phone = models.CharField(max_length=16, validators=[phone_validator])
    latitude = models.DecimalField(
        max_digits=8, decimal_places=6, validators=latitude_validators,
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, validators=longitude_validators,
    )
    is_24x7 = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    demo_key = models.SlugField(
        max_length=50, unique=True, null=True, blank=True, editable=False,
        help_text="Stable identifier for generated FAKE sample data; blank for ordinary facilities.",
    )

    @property
    def is_demo(self):
        return self.demo_key is not None

    class Meta:
        ordering = ["name", "pk"]
        indexes = [models.Index(fields=["facility_type", "is_active"])]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    latitude__gte=-90, latitude__lte=90,
                    longitude__gte=-180, longitude__lte=180,
                ),
                name="facility_valid_coordinates",
            ),
        ]

    def __str__(self):
        return self.name
