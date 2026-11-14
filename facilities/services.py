from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q

from .models import Facility
from .live import LiveFacility, nearby_listings, normalise_phone, parse_facility

EARTH_RADIUS_KM = 6371.0088
PAGE_SIZE = 20


def haversine_km(latitude, longitude, other_latitude, other_longitude):
    """Great-circle distance, not a road distance or an ambulance ETA."""
    lat1, lat2 = radians(float(latitude)), radians(float(other_latitude))
    delta_lat = lat2 - lat1
    delta_lon = radians(float(other_longitude) - float(longitude))
    a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    # Floating-point rounding near antipodes can otherwise put a above 1.
    return 2 * EARTH_RADIUS_KM * asin(sqrt(max(0.0, min(1.0, a))))


@dataclass(frozen=True)
class FacilityMatch:
    facility: Facility | LiveFacility
    distance_km: float | None

    @property
    def call_url(self):
        phone = normalise_phone(self.facility.phone)
        if self.facility.is_demo or not phone:
            return None
        return f"tel:{phone}"

    @property
    def source(self):
        return getattr(self.facility, "source", "Local directory")

    @property
    def source_url(self):
        return getattr(self.facility, "source_url", None)

    @property
    def opening_hours(self):
        return getattr(self.facility, "opening_hours", "24/7" if self.facility.is_24x7 else "")

    @property
    def directions_url(self):
        if self.facility.is_demo:
            return None
        query = urlencode({
            "api": 1,
            "destination": f"{self.facility.latitude},{self.facility.longitude}",
        })
        return f"https://www.google.com/maps/dir/?{query}"


def search_facilities(cleaned_data):
    """Filter in SQL; calculate and sort distances in Python for SQLite portability.

    For a large catalogue, replace this service with an indexed PostGIS query.
    Pagination limits the response, but this SQLite service still computes each
    matching candidate's distance before pagination.
    """
    queryset = Facility.objects.filter(is_active=True, demo_key__isnull=True).prefetch_related("specialities")
    if query := cleaned_data.get("q"):
        queryset = queryset.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
            | Q(specialities__name__icontains=query)
        ).distinct()
    if facility_type := cleaned_data.get("facility_type"):
        queryset = queryset.filter(facility_type=facility_type)
    if speciality := cleaned_data.get("speciality"):
        queryset = queryset.filter(specialities__slug=speciality)
    if cleaned_data.get("open_24x7"):
        queryset = queryset.filter(is_24x7=True)

    latitude, longitude = cleaned_data.get("latitude"), cleaned_data.get("longitude")
    radius = cleaned_data.get("radius_km")
    metadata = {"provider": "OpenStreetMap", "status": "not_requested", "retrieved_at": None,
                "message": "", "radius_km": radius, "truncated": False}
    if settings.FACILITIES_LIVE_ENABLED and latitude is not None:
        radius = radius or 5
        metadata["radius_km"] = radius
    matches = []
    for facility in queryset:
        distance = None
        if latitude is not None and longitude is not None:
            distance = haversine_km(latitude, longitude, facility.latitude, facility.longitude)
        if radius is None or (distance is not None and distance <= radius):
            matches.append(FacilityMatch(facility, distance))
    if settings.FACILITIES_LIVE_ENABLED and latitude is not None:
        payload, status, message = nearby_listings(latitude, longitude, radius)
        metadata.update(status=status, message=message)
        if payload is not None:
            metadata.update(retrieved_at=payload["retrieved_at"], truncated=payload["truncated"])
            seen = set()
            for element in payload["elements"]:
                facility = parse_facility(element)
                if facility is None or facility.pk in seen:
                    continue
                seen.add(facility.pk)
                if facility_type and facility.facility_type != facility_type:
                    continue
                labels = [item.name for item in facility.specialities.all()]
                if query and query.casefold() not in " ".join([facility.name, facility.address, *labels]).casefold():
                    continue
                if speciality:
                    needle = speciality.replace("-", " ").replace("_", " ").casefold()
                    aliases = {"emergency care": "emergency", "general medicine": "general"}
                    needle = aliases.get(needle, needle)
                    if not any(needle == label.casefold() for label in labels):
                        continue
                if cleaned_data.get("open_24x7") and not facility.is_24x7:
                    continue
                distance = haversine_km(latitude, longitude, facility.latitude, facility.longitude)
                if distance > radius:
                    continue
                # OSM may map both a building and a point for the same named facility.
                if any(existing.facility.name.casefold() == facility.name.casefold()
                       and existing.facility.facility_type == facility.facility_type
                       and haversine_km(existing.facility.latitude, existing.facility.longitude,
                                        facility.latitude, facility.longitude) < .1 for existing in matches):
                    continue
                matches.append(FacilityMatch(facility, distance))
    if latitude is not None and longitude is not None:
        matches.sort(key=lambda match: (
            match.distance_km, match.facility.name.casefold(), str(match.facility.pk),
        ))
    else:
        matches.sort(key=lambda match: (match.facility.name.casefold(), match.facility.pk))
    page = Paginator(matches, PAGE_SIZE).page(cleaned_data.get("page") or 1)
    page.search_metadata = metadata
    return page
