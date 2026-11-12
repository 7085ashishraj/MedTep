from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Q

from .models import Facility

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
    facility: Facility
    distance_km: float | None

    @property
    def call_url(self):
        if self.facility.is_demo or not self.facility.phone.strip("+0"):
            return None
        return f"tel:{self.facility.phone}"

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
    Pagination limits the response, but this learning version still computes each
    matching candidate's distance before pagination.
    """
    queryset = Facility.objects.filter(is_active=True).prefetch_related("specialities")
    if query := cleaned_data.get("q"):
        queryset = queryset.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
            | Q(specialities__name__icontains=query)
        ).distinct()
    if facility_type := cleaned_data.get("facility_type"):
        queryset = queryset.filter(facility_type=facility_type)
    if speciality := cleaned_data.get("speciality"):
        queryset = queryset.filter(specialities=speciality)
    if cleaned_data.get("open_24x7"):
        queryset = queryset.filter(is_24x7=True)

    latitude, longitude = cleaned_data.get("latitude"), cleaned_data.get("longitude")
    radius = cleaned_data.get("radius_km")
    matches = []
    for facility in queryset:
        distance = None
        if latitude is not None and longitude is not None:
            distance = haversine_km(latitude, longitude, facility.latitude, facility.longitude)
        if radius is None or (distance is not None and distance <= radius):
            matches.append(FacilityMatch(facility, distance))
    if latitude is not None and longitude is not None:
        matches.sort(key=lambda match: (
            match.distance_km, match.facility.name.casefold(), match.facility.pk,
        ))
    else:
        matches.sort(key=lambda match: (match.facility.name.casefold(), match.facility.pk))
    return Paginator(matches, PAGE_SIZE).page(cleaned_data.get("page") or 1)
