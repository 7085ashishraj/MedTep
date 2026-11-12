from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone

from facilities.models import Facility

from .models import AmbulanceRequest, AmbulanceStatusEvent, EmergencyRequest
from .permissions import can_operate

STATUS_ORDER = list(AmbulanceRequest.Status.values)


def allowed_statuses(current):
    index = STATUS_ORDER.index(current)
    return STATUS_ORDER[index:index + 2]


@transaction.atomic
def request_ambulance(*, user, emergency_pk):
    emergency = get_object_or_404(EmergencyRequest.objects.select_for_update(), pk=emergency_pk, user=user)
    existing = AmbulanceRequest.objects.filter(emergency=emergency).first()
    if existing:
        return existing, False
    if emergency.status != EmergencyRequest.Status.ACTIVE:
        raise ValidationError("Only an active SOS record can start a new ambulance request.")
    ambulance, created = AmbulanceRequest.objects.get_or_create(emergency=emergency)
    if created:
        AmbulanceStatusEvent.objects.create(
            ambulance=ambulance, status=ambulance.status, changed_by=user,
        )
    return ambulance, created


@transaction.atomic
def update_ambulance(*, operator, pk, expected_version, status, facility, operator_notes):
    if not can_operate(operator):
        raise PermissionDenied("Operator access is required.")
    ambulance = get_object_or_404(AmbulanceRequest, pk=pk)
    if ambulance.version != expected_version:
        raise ValidationError("Another operator changed this request. Reload the latest version before saving.", code="stale")
    if status not in allowed_statuses(ambulance.status):
        raise ValidationError("Move one step forward at a time; completed requests cannot be reopened.")
    if len(operator_notes) > 2000:
        raise ValidationError("Keep internal notes within 2000 characters.")
    if facility and facility.pk != ambulance.facility_id:
        # Re-check at save time in case the directory changed after form validation.
        facility = get_object_or_404(Facility, pk=facility.pk)
        if not facility.is_active or facility.facility_type not in (Facility.Type.HOSPITAL, Facility.Type.CLINIC):
            raise ValidationError("Choose an active hospital or clinic as the facility reference.")
    changed = AmbulanceRequest.objects.filter(pk=pk, version=expected_version).update(
        status=status, facility=facility, operator_notes=operator_notes,
        version=F("version") + 1, updated_at=timezone.now(),
    )
    if changed != 1:
        raise ValidationError("Another operator changed this request. Reload before saving.", code="stale")
    if status != ambulance.status:
        AmbulanceStatusEvent.objects.create(ambulance=ambulance, status=status, changed_by=operator)
    ambulance.refresh_from_db()
    return ambulance


def ambulance_snapshot(ambulance):
    events = {event.status: event.created_at for event in ambulance.status_events.all()}
    current = STATUS_ORDER.index(ambulance.status)
    return {
        "id": ambulance.pk, "status": ambulance.status,
        "status_label": ambulance.get_status_display(), "version": ambulance.version,
        "updated_at": ambulance.updated_at,
        "facility": {"name": ambulance.facility.name, "is_demo": ambulance.facility.is_demo} if ambulance.facility_id else None,
        "timeline": [{
            "status": value, "label": label, "is_current": index == current,
            "is_reached": index <= current, "recorded_at": events.get(value),
        } for index, (value, label) in enumerate(AmbulanceRequest.Status.choices)],
    }
