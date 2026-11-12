import re
from dataclasses import dataclass
from urllib.parse import quote, urlencode

from django.core.exceptions import PermissionDenied
from django.utils import timezone

from .models import EmergencyRequest


def save_sos_request(*, user, request_id, latitude, longitude):
    """A retry with the same UUID returns the same owned record, without dispatch."""
    emergency, created = EmergencyRequest.objects.get_or_create(
        pk=request_id,
        defaults={"user": user, "latitude": latitude, "longitude": longitude},
    )
    if emergency.user_id != user.pk:
        raise PermissionDenied("This request identifier is unavailable. Open the SOS page again.")
    return emergency, created


def google_maps_url(emergency):
    query = urlencode({"api": 1, "query": f"{emergency.latitude},{emergency.longitude}"})
    return f"https://www.google.com/maps/search/?{query}"


def build_emergency_message(emergency):
    recorded = timezone.localtime(emergency.created_at).strftime("%d %b %Y, %H:%M %Z")
    return (
        "I need urgent medical help. Please call me and help me contact emergency services.\n"
        f"My recorded location: {google_maps_url(emergency)}\n"
        f"Saved: {recorded}. This is a location snapshot, not live tracking.\n"
        "This message does not book an ambulance."
    )


@dataclass(frozen=True)
class ShareOptions:
    whatsapp_url: str | None
    sms_url: str | None


def build_share_options(message, phone=None):
    """Transport boundary: prepare composers only; never send a message.

    A later Twilio adapter can accept the same message and recipient, but actual
    sending must be a separate, explicitly authorised POST operation.
    """
    encoded = quote(message, safe="")
    if phone is None:
        return ShareOptions(f"https://wa.me/?text={encoded}", f"sms:?body={encoded}")
    if not re.fullmatch(r"\+?[0-9]{7,15}", phone) or not phone.strip("+0"):
        return ShareOptions(None, None)
    whatsapp = None
    # Never guess a country code from a local number.
    if re.fullmatch(r"\+[1-9][0-9]{7,14}", phone):
        whatsapp = f"https://wa.me/{phone[1:]}?text={encoded}"
    return ShareOptions(whatsapp, f"sms:{phone}?body={encoded}")
