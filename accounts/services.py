from django.db import transaction
from django.utils import timezone

from .models import EmergencyContact, MedicalProfile


@transaction.atomic
def save_emergency_contact(*, profile, data, contact=None):
    """Save one owned contact and switch the primary contact atomically."""
    profile = MedicalProfile.objects.select_for_update().get(pk=profile.pk)
    if contact is None:
        contact = EmergencyContact(profile=profile)
    elif contact.profile_id != profile.pk:
        raise ValueError("The contact must belong to this profile.")

    if data["is_primary"]:
        profile.emergency_contacts.filter(is_primary=True).exclude(pk=contact.pk).update(
            is_primary=False, updated_at=timezone.now(),
        )
    for field in ("name", "relationship", "phone", "is_primary"):
        setattr(contact, field, data[field])
    contact.full_clean()
    contact.save()
    return contact
