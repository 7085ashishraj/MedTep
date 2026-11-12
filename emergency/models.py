import uuid

from django.conf import settings
from django.db import models

from common.models import TimeStampedModel
from common.validators import latitude_validators, longitude_validators


class EmergencyRequest(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RESOLVED = "resolved", "Resolved"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emergency_requests",
    )
    latitude = models.DecimalField(
        max_digits=8, decimal_places=6, validators=latitude_validators,
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, validators=longitude_validators,
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE,
    )

    class Meta:
        ordering = ["-created_at", "pk"]
        indexes = [models.Index(fields=["status", "created_at"])]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    latitude__gte=-90, latitude__lte=90,
                    longitude__gte=-180, longitude__lte=180,
                ),
                name="emergency_valid_coordinates",
            ),
        ]

    def __str__(self):
        return f"SOS {self.pk} ({self.get_status_display()})"


class AmbulanceRequest(TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        ACCEPTED = "accepted", "Accepted"
        ON_THE_WAY = "on_the_way", "On the way"
        COMPLETED = "completed", "Completed"

    emergency = models.OneToOneField(
        EmergencyRequest, on_delete=models.CASCADE, related_name="ambulance_request",
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ambulance_requests",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.REQUESTED,
    )
    operator_notes = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ["-created_at", "pk"]
        indexes = [models.Index(fields=["status", "created_at"])]

    def __str__(self):
        return f"Ambulance for {self.emergency_id} ({self.get_status_display()})"


class AmbulanceStatusEvent(models.Model):
    ambulance = models.ForeignKey(
        AmbulanceRequest, on_delete=models.CASCADE, related_name="status_events",
    )
    status = models.CharField(max_length=20, choices=AmbulanceRequest.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="ambulance_status_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]
        constraints = [models.UniqueConstraint(
            fields=["ambulance", "status"], name="one_ambulance_event_per_status",
        )]

    def __str__(self):
        return f"{self.ambulance_id}: {self.get_status_display()}"
