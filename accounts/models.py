from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import TimeStampedModel
from common.validators import phone_validator


class User(AbstractUser):
    """Keep Django authentication; allow future user fields without replacing it."""


class MedicalProfile(TimeStampedModel):
    class BloodGroup(models.TextChoices):
        UNKNOWN = "unknown", "Unknown"
        A_POSITIVE = "A+", "A positive"
        A_NEGATIVE = "A-", "A negative"
        B_POSITIVE = "B+", "B positive"
        B_NEGATIVE = "B-", "B negative"
        AB_POSITIVE = "AB+", "AB positive"
        AB_NEGATIVE = "AB-", "AB negative"
        O_POSITIVE = "O+", "O positive"
        O_NEGATIVE = "O-", "O negative"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_profile",
    )
    blood_group = models.CharField(
        max_length=7, choices=BloodGroup.choices, default=BloodGroup.UNKNOWN,
    )
    allergies = models.TextField(blank=True, help_text="Blank means not recorded.")
    medical_conditions = models.TextField(blank=True)

    def __str__(self):
        return f"Medical profile for {self.user.username}"


class EmergencyContact(TimeStampedModel):
    profile = models.ForeignKey(
        MedicalProfile, on_delete=models.CASCADE, related_name="emergency_contacts",
    )
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=16, validators=[phone_validator])
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "name", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile"],
                condition=models.Q(is_primary=True),
                name="one_primary_contact_per_profile",
            ),
        ]

    def __str__(self):
        return self.name
