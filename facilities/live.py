"""Bounded, cached OpenStreetMap healthcare lookups; never invent listing details."""
from dataclasses import dataclass
from hashlib import sha256
import json
import logging
from math import isfinite
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import caches
from django.utils import timezone

from .models import Facility

MAX_ELEMENTS = 2000
MAX_BYTES = 4 * 1024 * 1024
FRESH_SECONDS = 15 * 60
STALE_SECONDS = 24 * 60 * 60
REQUEST_TIMEOUT = 45
logger = logging.getLogger(__name__)


class ProviderUnavailable(Exception):
    def __init__(self, message, *, retryable=True):
        super().__init__(message)
        self.retryable = retryable


def provider_endpoints():
    """Keep explicit provider order, with no duplicate or unbounded attempts."""
    return tuple(dict.fromkeys([
        settings.FACILITIES_OVERPASS_URL,
        *(url.strip() for url in settings.FACILITIES_OVERPASS_FALLBACK_URLS if url.strip()),
    ]))[:3]


class Specialities:
    """Small read-only collection with the same interface used by our templates."""
    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values


@dataclass(frozen=True)
class SpecialityLabel:
    name: str


@dataclass(frozen=True)
class LiveFacility:
    pk: str
    name: str
    facility_type: str
    address: str
    phone: str
    latitude: float
    longitude: float
    specialities: Specialities
    is_24x7: bool
    opening_hours: str
    source_url: str
    is_demo: bool = False
    source: str = "OpenStreetMap"

    def get_facility_type_display(self):
        return Facility.Type(self.facility_type).label


def clean_text(value, limit=250):
    return " ".join(value.split())[:limit] if isinstance(value, str) else ""


def normalise_phone(value):
    # Accept just one clearly usable number; never fabricate or guess a country code.
    for candidate in clean_text(value).split(";"):
        candidate = re.sub(r"[\s().-]", "", candidate)
        if re.fullmatch(r"\+?[0-9]{7,15}", candidate) and candidate.strip("+0"):
            return candidate
    return ""


def parse_facility(element):
    if not isinstance(element, dict):
        return None
    tags = element.get("tags")
    kind, identifier = element.get("type"), element.get("id")
    if not isinstance(tags, dict) or kind not in ("node", "way", "relation") or type(identifier) is not int or identifier <= 0:
        return None
    if tags.get("access") in ("no", "private") or tags.get("disused") == "yes" or tags.get("abandoned") == "yes":
        return None
    if tags.get("healthcare") in ("blood_bank", "blood_donation") or tags.get("amenity") in ("blood_bank", "blood_donation"):
        category = "blood_bank"
    else:
        mapping = {"hospital": "hospital", "clinic": "clinic", "doctor": "clinic", "doctors": "clinic", "pharmacy": "pharmacy"}
        category = mapping.get(tags.get("healthcare")) or mapping.get(tags.get("amenity"))
    if not category:
        return None
    coordinates = element if kind == "node" else element.get("center")
    if not isinstance(coordinates, dict):
        return None
    try:
        latitude, longitude = float(coordinates["lat"]), float(coordinates["lon"])
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
    if not isfinite(latitude) or not isfinite(longitude) or abs(latitude) > 90 or abs(longitude) > 180:
        return None
    name = clean_text(tags.get("name")) or clean_text(tags.get("name:en"))
    if not name:
        name = f"Unnamed {Facility.Type(category).label.lower()} (mapped listing)"
    street = " ".join(filter(None, (clean_text(tags.get("addr:housenumber")), clean_text(tags.get("addr:street")))))
    address = clean_text(tags.get("addr:full"), 500) or ", ".join(filter(None, (
        street, clean_text(tags.get("addr:suburb")), clean_text(tags.get("addr:city")), clean_text(tags.get("addr:postcode")),
    ))) or "Street address not provided — use Directions for the mapped location."
    specialities = clean_text(tags.get("healthcare:speciality"))
    labels = [SpecialityLabel(value.replace("_", " ").strip().title()) for value in specialities.split(";") if value.strip()]
    hours = clean_text(tags.get("opening_hours"))
    return LiveFacility(
        pk=f"osm-{kind}-{identifier}", name=name, facility_type=category, address=address,
        phone=normalise_phone(tags.get("contact:phone") or tags.get("phone")), latitude=latitude, longitude=longitude,
        specialities=Specialities(labels), is_24x7=hours == "24/7", opening_hours=hours,
        source_url=f"https://www.openstreetmap.org/{kind}/{identifier}",
    )


def request_elements(latitude, longitude, radius_km, *, endpoint=None):
    endpoint = settings.FACILITIES_OVERPASS_URL if endpoint is None else endpoint
    try:
        parsed = urlsplit(endpoint)
    except ValueError as error:
        raise ProviderUnavailable("The directory provider needs a valid HTTPS endpoint.", retryable=False) from error
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ProviderUnavailable("The directory provider needs a valid HTTPS endpoint.", retryable=False)
    if settings.FACILITIES_OVERPASS_METHOD not in ("GET", "POST"):
        raise ProviderUnavailable("The directory request method must be GET or POST.", retryable=False)
    # Only numeric, validated values enter the query. No search strings, names or user IDs are sent.
    metres = int(radius_km * 1000) + 800  # Cover rounding to a coarse ~1 km search grid.
    area = f"(around:{metres},{latitude:.2f},{longitude:.2f})"
    selectors = {
        "amenity": ("hospital", "clinic", "doctors", "pharmacy", "blood_bank", "blood_donation"),
        "healthcare": ("hospital", "clinic", "doctor", "pharmacy", "blood_bank", "blood_donation"),
    }
    body = "".join(f'nwr["{key}"~"^({"|".join(values)})$"]{area};' for key, values in selectors.items())
    query = f'[out:json][timeout:12];({body});out center tags {MAX_ELEMENTS};'
    encoded = urlencode({"data": query})
    use_post = settings.FACILITIES_OVERPASS_METHOD == "POST"
    headers = {
        "User-Agent": "MEDTAP/1.0 (+https://github.com/7085ashishraj/MedTep)",
        "Accept": "application/json",
    }
    if use_post:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = Request(endpoint if use_post else endpoint + "?" + encoded, data=encoded.encode() if use_post else None, headers=headers)
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ProviderUnavailable("The directory response was too large. Try a smaller radius.")
        payload = json.loads(raw)
        if not isinstance(payload, dict) or payload.get("remark") or not isinstance(payload.get("elements"), list):
            raise ProviderUnavailable("The directory returned an incomplete response.")
        return {"elements": payload["elements"][:MAX_ELEMENTS], "retrieved_at": timezone.now().isoformat(),
                "truncated": len(payload["elements"]) >= MAX_ELEMENTS, "provider_host": parsed.hostname}
    except HTTPError as error:
        if error.code in (429, 500, 502, 503, 504):
            message = "The live directory servers are busy. Please try again in a minute."
        else:
            message = "The directory provider rejected the request. Please check the server configuration."
        raise ProviderUnavailable(message, retryable=error.code in (429, 500, 502, 503, 504)) from error
    except TimeoutError as error:
        raise ProviderUnavailable("The directory search timed out. Please try again shortly.") from error
    except (URLError, OSError, ValueError) as error:
        # Do not reflect upstream bodies, endpoint credentials or the user's coordinates in public errors/logs.
        raise ProviderUnavailable("The live directory is temporarily unavailable. Please try again shortly.") from error


def nearby_listings(latitude, longitude, radius_km):
    """Reuse area snapshots; expose age and outages, never silently return fake data."""
    latitude, longitude = round(latitude, 2), round(longitude, 2)
    endpoints = provider_endpoints()
    # Changing provider priority must not discard a usable snapshot for the same area.
    signature = f"v2:{tuple(sorted(endpoints, reverse=True))}:{latitude:.2f}:{longitude:.2f}:{radius_km:.3f}"
    key = "osm:" + sha256(signature.encode()).hexdigest()
    cache = caches["facilities"]
    fresh = cache.get(key)
    if fresh is not None:
        return fresh, "cached", ""
    stale = cache.get(key + ":stale")
    available = [(endpoint, "osm:cooldown:" + sha256(endpoint.encode()).hexdigest()) for endpoint in endpoints]
    available = [(endpoint, key) for endpoint, key in available if not cache.get(key)]
    if not available:
        return stale, "stale" if stale else "unavailable", "The directory is busy. Please try again in a minute."
    # A shared filesystem directory is an atomic, cross-process in-flight guard.
    lock = Path(settings.FACILITIES_LOCK_DIR)
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        if lock.exists() and time.time() - lock.stat().st_mtime > REQUEST_TIMEOUT * len(endpoints) + 30:
            lock.rmdir()  # Recover an abandoned request after a process stopped.
        lock.mkdir()
    except (FileExistsError, FileNotFoundError):
        return stale, "stale" if stale else "unavailable", "Another directory search is loading. Please try again shortly."
    try:
        # Another worker may have filled the cache while this request acquired the guard.
        fresh = cache.get(key)
        if fresh is not None:
            return fresh, "cached", ""
        message = "The live directory is temporarily unavailable. Please try again shortly."
        for endpoint, cooldown_key in available:
            try:
                payload = request_elements(latitude, longitude, radius_km, endpoint=endpoint)
            except ProviderUnavailable as error:
                if error.retryable:
                    cache.set(cooldown_key, True, 60)
                message = str(error)
                # Log useful diagnostics without coordinates, credentials or upstream bodies.
                cause = error.__cause__
                try:
                    host = urlsplit(endpoint).hostname
                except ValueError:
                    host = "invalid endpoint"
                logger.warning("Healthcare directory failed: host=%s, error=%s, status=%s",
                               host, type(cause).__name__ if cause else type(error).__name__,
                               getattr(cause, "code", None))
                if not error.retryable:
                    break
                continue
            cache.set(key, payload, FRESH_SECONDS)
            cache.set(key + ":stale", payload, STALE_SECONDS)
            return payload, "fresh", ""
        return stale, "stale" if stale else "unavailable", message
    finally:
        try:
            lock.rmdir()
        except FileNotFoundError:
            pass
