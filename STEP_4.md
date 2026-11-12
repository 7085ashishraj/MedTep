# Step 4 — Nearby facilities, filters and a map

This step is implemented in your workspace. Finish this feature before moving to
SOS. Existing accounts, medical profiles and contacts are unchanged. This guide
contains complete current files, so you can study or reproduce each change.
Steps 1–3 are prerequisites. Older guides preserve their step's code; use this
guide for the current home-page/search files.

## What you have now

- A public facility directory with name/address/speciality text search, facility
  type, speciality, 24×7 and optional radius filters.
- Browser location requested only on a tap, manual coordinates and a demo centre.
- Haversine distance sorting, with zero distance handled correctly. Without a
  location, facilities sort A–Z and distance remains unknown.
- Responsive list/map layout. Numbered pins match the current page's cards.
- A read-only DRF endpoint ready for a later mobile client.
- Clear FAKE badges; demo phone/directions actions are disabled in the page and
  null in the API. Only active facilities are public.

## Files added or changed

```text
MEDTAP/
├── core/
│   ├── forms.py                     # small home-page search form
│   └── views.py                     # working quick-action links
├── facilities/
│   ├── forms.py                     # shared search validation
│   ├── services.py                  # distance calculation and ordered results
│   ├── serializers.py               # explicit public API fields
│   ├── views.py                     # consistent function-based views
│   ├── urls.py                      # HTML and API routes
│   ├── test_nearby.py                # 25 new Django tests
│   └── frontend_tests.cjs            # 9 isolated JavaScript checks
├── templates/
│   ├── core/home.html
│   ├── facilities/nearby.html
│   └── partials/
│       ├── facility_card.html
│       ├── location_button.html
│       ├── action_card.html
│       ├── navbar.html
│       └── footer.html
└── static/
    ├── css/theme.css                 # existing palette plus finder styles
    ├── js/
    │   ├── location.js               # shared by home and finder
    │   └── facilities.js             # Leaflet map and safe popups
    └── vendor/leaflet/               # pinned library, images and license
```

Remove `static/js/home.js` from the previous preview. It has been replaced by
`location.js`; do not load both. `base.html`, authentication and the data models
remain as delivered previously. No additional Python dependency or secret is needed.

## Exact commands — PowerShell

Run from the MEDTAP directory in VS Code. Activation is optional because these
commands address the virtual environment's interpreter directly.

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo_facilities
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test facilities accounts
node facilities/frontend_tests.cjs
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

No new migration is required for this step. `migrate` should report no migrations
to apply if Steps 1–3 are complete. The seed command preserves existing demo edits.
Expect **85 Django tests passing** and **9 frontend checks passing**. Node is only
needed to run the isolated JavaScript checks, not to run Django. If a development
server is already running, use that terminal or stop it with Ctrl+C before
starting another server on the same port. PythonAnywhere/Render setup comes later.

An admin account is optional for browsing. To manage facility records if you
have not already created one:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

## Try it in your browser

1. Open [Find care](http://127.0.0.1:8000/facilities/). With the unchanged seed,
   you should see **7 active facilities**, all labelled FAKE. The inactive sample
   pharmacy is excluded. Without a location the list is alphabetical.
2. Tap **Try demo location**. It uses latitude `12.970000`, longitude `77.590000`
   with a 5 km radius. FAKE Demo Hospital Alpha should be first at **0.00 km**.
3. Choose **Hospital** and **Cardiology**, then **Find care**. One FAKE hospital
   should match. The filters combine using AND.
4. Tap **On map**. Its numbered pin opens a popup with a link back to the card.
   The pin and popup both identify the FAKE sample.
5. Clear filters and try a name or address without coordinates. This works even
   without JavaScript. It matches your stored data, not an external geocoder.
6. Tap **Use my location** if you want to share your real location. You may need
   to allow browser permission. A denied request leaves manual entry, name search
   and the demo link usable. There may be no samples near your real location.
7. On a phone, filters and cards stack, the map follows the list and the Call 112
   bar remains available. All demo call/directions controls stay disabled.

Distance is an approximate straight-line distance, not driving distance or travel
time. Listed 24×7 hours do not establish current availability, beds, stock or
emergency capacity. Ordinary admin entries are not independently verified.

## API for a future mobile app

Endpoint: `GET /facilities/api/nearby/`. It is intentionally public and read-only;
the project's default authenticated permission still applies elsewhere. It does
not return medical profiles, contacts, internal demo keys or operator notes.

| Parameter | Meaning |
| --- | --- |
| `q` | Optional text, maximum 120 characters; name, address or speciality name |
| `facility_type` | `hospital`, `clinic`, `pharmacy` or `blood_bank` |
| `speciality` | A speciality slug, for example `cardiology` |
| `open_24x7` | `true` to include only entries flagged 24×7; omit for all |
| `latitude`, `longitude` | Both optional, but supply both together; ranges −90…90 and −180…180 |
| `radius_km` | Optional 0.1…500 km, requires coordinates |
| `page` | Optional positive page number; 20 results per page |

```powershell
$nearbyResponse = Invoke-RestMethod 'http://127.0.0.1:8000/facilities/api/nearby/?latitude=12.97&longitude=77.59&radius_km=5'
$nearbyResponse.count
$nearbyResponse.results | Select-Object name, distance_km, is_demo, call_url
```

With unchanged demo data the count is 7. Results are ordered nearest first.
Response keys are `count`, `page`, `pages`, `next`, `previous`, `results`.
Each result exposes ID, name, facility type/label, address, coordinates,
speciality names, 24×7 flag, demo flag, distance, phone and action URLs.
Coordinates and distance are JSON numbers. Unknown distance and demo phone/action
URLs are JSON null. Invalid filters produce HTTP 400 with field errors, missing
pages produce 404 and POST is rejected with 405. Empty searches return 200 with
an empty results list. API pagination URLs preserve filters.

## How to explain it in your viva

**Form → service → view → presentation.** The form validates raw query parameters.
The service selects active records, applies database filters, calculates distances
and sorts them. HTML and API views call that same service, so their answers match.
Django templates render cards; a DRF serializer exposes only explicit public fields.

**Haversine:** convert latitude/longitude to radians; calculate
`a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)` and
`distance = 2 × R × asin(√a)`, using `R = 6371.0088 km`.
Clamping `a` to [0,1] prevents a floating-point domain error near opposite points.
Test `is not None` rather than truthiness because latitude/longitude/distance can
legitimately be zero. This formula crosses the international date line correctly.

**SQLite today, PostGIS later:** Django handles text/type/speciality filters in
SQL. Python calculates distances before pagination, which is appropriate for this
small learning catalogue. Pagination bounds response size, not calculation work:
every filtered candidate is still evaluated. For a large catalogue, replace this
service with indexed PostGIS distance queries and keep the view/API contract.
`prefetch_related` avoids one speciality query per card.

**Security and ownership:** search is a read-only GET operation, so it does not
need a CSRF token. Existing state-changing account/admin forms retain CSRF and
authentication checks. Public access applies only to facility search. Names are
escaped by Django; map payloads use `json_script`; popup text uses `textContent`
rather than interpolating facility data into HTML. No dummy dial/navigation URLs
are exposed for demo records.

**Location and maps:** coordinates are requested only on a tap. GET searches send
them to Django in a URL, which may appear in history, server/proxy logs and copied
links. Search does not persist them in a medical profile or EmergencyRequest.
The response uses no-store caching; production logging should redact coordinates
as part of deployment work. OpenStreetMap receives requests for the viewed area.
Do not describe this as wholly local or anonymous. No location permission is
granted during automated checks; isolated mocks cover success/failure paths.

## Leaflet assets and map policy

Leaflet 1.9.4 is the stable release used here; 2.0 is a prerelease according to the
[official versioned reference](https://leafletjs.com/reference-1.9.4.html).
Its files and license are already in `static/vendor/leaflet/`. If recreating the
project from this guide, download the official pinned package assets:

```powershell
New-Item -ItemType Directory -Force static/vendor/leaflet/images | Out-Null
$leafletFiles = @('leaflet.js', 'leaflet.css', 'images/layers.png', 'images/layers-2x.png', 'images/marker-icon.png', 'images/marker-icon-2x.png', 'images/marker-shadow.png')
foreach ($leafletFile in $leafletFiles) {
    Invoke-WebRequest -UseBasicParsing "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/$leafletFile" -OutFile "static/vendor/leaflet/$leafletFile"
}
Invoke-WebRequest -UseBasicParsing 'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/LICENSE' -OutFile static/vendor/leaflet/LICENSE
```

The library loads locally. Map tiles still require internet access. The
[OpenStreetMap tile policy](https://operations.osmfoundation.org/policies/tiles/)
requires visible attribution and normal caching, with no bulk/offline download.
The finder sets an origin-only cross-domain Referrer-Policy so OSM gets a valid
Referer without receiving search coordinates in it. It has a useful list fallback
for tile/library failures. Review provider capacity before a public deployment.
Our custom files have no inline styles; Leaflet itself positions map layers using
its own runtime style attributes.

## Validation completed

- 85 Django tests: existing account/admin/seed tests plus 25 search tests for
  zero/boundary/invalid coordinates, Haversine edge cases, filter combinations,
  stable sorting, pagination, escaping, public read-only API and demo protection.
- 9 JavaScript checks using isolated browser-API mocks: explicit-tap location,
  loading state, rounded/zero coordinates, permission denial, timeout, invalid
  values, unsupported context, safe popup text and map failure fallback.
- Django system checks and migration-drift check pass; no new migration.
- Desktop and phone browser review: filters, map tiles, card-to-pin popup, fake
  actions disabled, visible attribution and phone layout without horizontal overflow.
  Live GPS accuracy and actual emergency calls were not exercised.

## Complete code, file by file

Create parent folders where necessary. Replace each file below in full. The
supporting vendor files above retain their supplied license; do not paste minified
library internals into your own scripts.

### `facilities/forms.py`

Validation stays identical between the browser page and API.

```python
from django import forms

from .models import Facility, Speciality


class FacilitySearchForm(forms.Form):
    """The HTML page and API deliberately accept the same search parameters."""

    q = forms.CharField(required=False, max_length=120, label="Name or address")
    facility_type = forms.ChoiceField(
        required=False, label="Facility type",
        choices=[("", "All facilities"), *Facility.Type.choices],
    )
    speciality = forms.ModelChoiceField(
        queryset=Speciality.objects.all(), to_field_name="slug", required=False,
        empty_label="All specialities",
    )
    open_24x7 = forms.BooleanField(required=False, label="24×7 only")
    latitude = forms.FloatField(required=False, min_value=-90, max_value=90)
    longitude = forms.FloatField(required=False, min_value=-180, max_value=180)
    radius_km = forms.FloatField(
        required=False, min_value=0.1, max_value=500, label="Within (km)",
        help_text="Optional, 0.1–500 km. Requires both coordinates.",
    )
    page = forms.IntegerField(required=False, min_value=1, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "open_24x7":
                field.widget.attrs["class"] = "form-check-input"
            elif not field.widget.is_hidden:
                field.widget.attrs["class"] = (
                    "form-select" if isinstance(field.widget, forms.Select) else "form-control"
                )
        self.fields["q"].widget.attrs["placeholder"] = "Hospital, pharmacy or address"
        for name in ("latitude", "longitude"):
            self.fields[name].widget.attrs.update({"step": "any", "inputmode": "decimal"})
        self.fields["radius_km"].widget.attrs.update({"step": "any", "placeholder": "Any distance"})

    def clean_q(self):
        return " ".join(self.cleaned_data["q"].split())

    def clean(self):
        data = super().clean()
        # Do not add a misleading pair error when a field already failed validation.
        if "latitude" in self.errors or "longitude" in self.errors:
            return data
        latitude, longitude = data.get("latitude"), data.get("longitude")
        if (latitude is None) != (longitude is None):
            raise forms.ValidationError("Enter both latitude and longitude, or leave both blank.")
        if data.get("radius_km") is not None and latitude is None:
            raise forms.ValidationError("Add a location before filtering by distance.")
        return data
```

### `facilities/services.py`

The portable distance/search service owns ordering and pagination.

```python
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
```

### `facilities/serializers.py`

Explicit public fields and null demo action URLs keep the API predictable.

```python
from rest_framework import serializers


class FacilityMatchSerializer(serializers.Serializer):
    """Only explicit public fields; dummy phone and action URLs are suppressed."""

    id = serializers.IntegerField(source="facility.pk")
    name = serializers.CharField(source="facility.name")
    facility_type = serializers.CharField(source="facility.facility_type")
    type_label = serializers.CharField(source="facility.get_facility_type_display")
    address = serializers.CharField(source="facility.address")
    latitude = serializers.FloatField(source="facility.latitude")
    longitude = serializers.FloatField(source="facility.longitude")
    specialities = serializers.SlugRelatedField(
        source="facility.specialities", many=True, read_only=True, slug_field="name",
    )
    is_24x7 = serializers.BooleanField(source="facility.is_24x7")
    is_demo = serializers.BooleanField(source="facility.is_demo")
    distance_km = serializers.FloatField(allow_null=True)
    phone = serializers.SerializerMethodField()
    call_url = serializers.CharField(allow_null=True)
    directions_url = serializers.CharField(allow_null=True)

    def get_phone(self, match):
        return None if match.facility.is_demo else match.facility.phone
```

### `facilities/views.py`

Function-based HTML and API views share validation and search results.

```python
from django.core.paginator import InvalidPage
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes, renderer_classes,
)
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .forms import FacilitySearchForm
from .serializers import FacilityMatchSerializer
from .services import search_facilities


def page_query(params, number):
    query = params.copy()
    query["page"] = number
    return "?" + query.urlencode()


@never_cache
@require_GET
def nearby(request):
    form = FacilitySearchForm(request.GET)
    page = None
    origin = None
    markers = []
    if form.is_valid():
        try:
            page = search_facilities(form.cleaned_data)
        except InvalidPage as error:
            raise Http404("That results page does not exist.") from error
        if form.cleaned_data["latitude"] is not None:
            origin = {"latitude": form.cleaned_data["latitude"], "longitude": form.cleaned_data["longitude"]}
        markers = FacilityMatchSerializer(page.object_list, many=True).data
    response = render(request, "facilities/nearby.html", {
        "form": form, "page_obj": page, "has_location": origin is not None,
        "map_data": {"origin": origin, "results": markers},
        "previous_query": page_query(request.GET, page.previous_page_number()) if page and page.has_previous() else None,
        "next_query": page_query(request.GET, page.next_page_number()) if page and page.has_next() else None,
    }, status=200 if not form.errors else 400)
    # OSM requires a Referer; send only our origin across domains, not coordinates.
    response["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@never_cache
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@renderer_classes([JSONRenderer])
def nearby_api(request):
    form = FacilitySearchForm(request.query_params)
    if not form.is_valid():
        return Response({"errors": dict(form.errors)}, status=400)
    try:
        page = search_facilities(form.cleaned_data)
    except InvalidPage as error:
        raise NotFound("That results page does not exist.") from error
    return Response({
        "count": page.paginator.count,
        "page": page.number,
        "pages": page.paginator.num_pages,
        "next": request.build_absolute_uri(page_query(request.query_params, page.next_page_number())) if page.has_next() else None,
        "previous": request.build_absolute_uri(page_query(request.query_params, page.previous_page_number())) if page.has_previous() else None,
        "results": FacilityMatchSerializer(page.object_list, many=True).data,
    })
```

### `facilities/urls.py`

App-level namespaced routes plug into the existing project URLs.

```python
from django.urls import path

from . import views

app_name = "facilities"
urlpatterns = [
    path("", views.nearby, name="nearby"),
    path("api/nearby/", views.nearby_api, name="nearby_api"),
]
```

### `core/forms.py`

The home-page query can be empty when using browser location.

```python
from django import forms


class CareSearchForm(forms.Form):
    """A small entry form; the facilities app validates submitted searches."""

    q = forms.CharField(
        label="Facility name or address",
        required=False,
        max_length=120,
        widget=forms.TextInput(attrs={
            "id": "care-query",
            "class": "form-control",
            "placeholder": "Hospital, pharmacy or address",
            "autocomplete": "off",
            "aria-describedby": "search-hint",
        }),
    )

    def clean_q(self):
        return " ".join(self.cleaned_data["q"].split())
```

### `core/views.py`

Home quick actions now lead to functional filtered searches.

```python
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET

from .forms import CareSearchForm


@require_GET
def home(request):
    search_form = CareSearchForm()
    facility_url = reverse("facilities:nearby")
    quick_actions = [
        {
            "key": "hospitals", "title": "Nearby Hospitals", "icon": "hospital",
            "description": "Find a place for the care you need.",
            "href": facility_url, "status": "Explore nearby care",
        },
        {
            "key": "ambulance", "title": "Ambulance", "icon": "truck-front",
            "description": "Request transport and follow its progress.",
            "preview_description": "Ambulance requests are not available in this preview. For immediate emergency assistance, call 112.",
            "critical": True,
        },
        {
            "key": "blood-banks", "title": "Blood Banks", "icon": "droplet",
            "description": "Look for blood banks in your area.", "tone": "teal",
            "href": facility_url + "?facility_type=blood_bank", "status": "Browse blood banks",
        },
        {
            "key": "pharmacies", "title": "Pharmacies", "icon": "capsule",
            "description": "Find a pharmacy close to you.", "tone": "teal",
            "href": facility_url + "?facility_type=pharmacy", "status": "Browse pharmacies",
        },
        {
            "key": "first-aid", "title": "First Aid", "icon": "bandaid",
            "description": "Clear, step-by-step guides for urgent moments.",
            "preview_description": "First-aid guides are not available in this preview. In a medical emergency, call 112 and follow the dispatcher's instructions.",
        },
        {
            "key": "helplines", "title": "Helplines", "icon": "telephone",
            "description": "Keep essential emergency numbers in reach.",
            "href": "#emergency-numbers", "available": True,
        },
    ]
    return render(request, "core/home.html", {
        "search_form": search_form,
        "quick_actions": quick_actions,
    })
```

### `templates/partials/location_button.html`

One accessible loading button is reused in both search forms.

```html
<button type="button" class="btn btn-outline-primary" data-location-button aria-describedby="location-feedback">
  <span class="spinner-border spinner-border-sm" data-location-spinner aria-hidden="true" hidden></span>
  {% include 'partials/icon.html' with name='geo-alt' class_name='icon-sm' only %}
  <span data-location-label>Use my location</span>
</button>
```

### `templates/partials/facility_card.html`

Reusable cards show distance, specialities and honest action availability.

```html
<article class="facility-card" id="facility-{{ match.facility.pk }}" tabindex="-1" aria-labelledby="facility-title-{{ match.facility.pk }}">
  <div class="facility-card-top"><span class="facility-number" aria-hidden="true">{{ number }}</span><span class="facility-type">{{ match.facility.get_facility_type_display }}</span>{% if match.facility.is_demo %}<span class="facility-demo-label">FAKE sample</span>{% endif %}</div>
  <h3 id="facility-title-{{ match.facility.pk }}">{{ match.facility.name }}</h3>
  <div class="facility-meta">{% if match.distance_km != None %}<span>{% include 'partials/icon.html' with name='geo-alt' class_name='icon-sm' only %} {{ match.distance_km|floatformat:2 }} km away</span>{% else %}<span>Distance needs a location</span>{% endif %}{% if match.facility.is_24x7 %}<span class="facility-hours">Listed as 24×7</span>{% endif %}</div>
  <p class="facility-address">{{ match.facility.address }}</p>
  <ul class="facility-specialities" aria-label="Specialities">{% for speciality in match.facility.specialities.all %}<li>{{ speciality.name }}</li>{% empty %}<li>Specialities not listed</li>{% endfor %}</ul>
  {% if match.facility.is_demo %}<p class="facility-demo-note">Learning data. This is not a real healthcare facility.</p>{% endif %}
  <div class="facility-card-actions">
    {% if match.call_url %}<a class="btn btn-primary" href="{{ match.call_url }}" aria-label="Call {{ match.facility.name }}">{% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call</a>{% else %}<button type="button" class="btn btn-outline-primary" disabled>Call unavailable</button>{% endif %}
    {% if match.directions_url %}<a class="btn btn-outline-primary" href="{{ match.directions_url }}" target="_blank" rel="noopener noreferrer" aria-label="Directions to {{ match.facility.name }} on Google Maps (opens in a new tab)">{% include 'partials/icon.html' with name='signpost-2' class_name='icon-sm' only %} Directions</a>{% else %}<button type="button" class="btn btn-outline-primary" disabled>Directions unavailable</button>{% endif %}
    <button type="button" class="facility-map-button" data-show-on-map="{{ match.facility.pk }}" aria-label="Show {{ match.facility.name }} on the map" hidden>On map {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</button>
  </div>
</article>
```

### `templates/facilities/nearby.html`

A single GET form works without JavaScript; the map enhances the list.

```html
{% extends 'base.html' %}
{% load static %}
{% block title %}Find nearby care | MEDTAP{% endblock %}
{% block extra_css %}<link rel="stylesheet" href="{% static 'vendor/leaflet/leaflet.css' %}">{% endblock %}
{% block content %}
<section class="finder-section">
  <div class="container">
    <header class="finder-heading">
      <div><p class="eyebrow">Care around you</p><h1>A clearer path.<br>A little closer.</h1><p>Explore hospitals, clinics, pharmacies and blood banks in one place.</p></div>
      <a class="btn btn-outline-primary" href="tel:112">{% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Urgent? Call 112</a>
    </header>
    <div class="finder-notice">{% include 'partials/icon.html' with name='info-circle' only %}<p><strong>A directory, not live availability.</strong> Listed hours and specialities do not confirm beds, medicines, blood stock or emergency capacity. FAKE samples are for learning only.</p></div>
    <form method="get" action="{% url 'facilities:nearby' %}" class="finder-filter-panel" data-location-form role="search" aria-label="Find facilities">
      {% include 'partials/form_errors.html' with form=form error_heading='Please check your search' only %}
      <div class="finder-filters">
        {% for field in form %}{% if field.name != 'latitude' and field.name != 'longitude' and field.name != 'page' and field.name != 'open_24x7' %}
        <div class="field-wrapper{% if field.name == 'q' %} finder-query{% endif %}">
          <label class="form-label" for="{{ field.id_for_label }}">{{ field.label }}</label>{{ field }}
          {% if field.help_text %}<div class="field-help" id="{{ field.auto_id }}_helptext">{{ field.help_text }}</div>{% endif %}
          {% if field.errors %}<ul class="field-errors" id="{{ field.auto_id }}_error">{% for error in field.errors %}<li>{{ error }}</li>{% endfor %}</ul>{% endif %}
        </div>
        {% endif %}{% endfor %}
      </div>
      <div class="finder-filter-actions">
        <label class="checkbox-label" for="{{ form.open_24x7.id_for_label }}">{{ form.open_24x7 }} <span>{{ form.open_24x7.label }}</span></label>
        <button type="submit" class="btn btn-primary">Find care {% include 'partials/icon.html' with name='search' class_name='icon-sm' only %}</button>
        <a class="finder-reset" href="{% url 'facilities:nearby' %}">Clear filters &amp; location</a>
      </div>
      <div class="finder-location">
        <div class="finder-location-actions">
          {% include 'partials/location_button.html' %}
          <a class="btn btn-outline-primary" href="{% url 'facilities:nearby' %}?latitude=12.970000&amp;longitude=77.590000&amp;radius_km=5">Try demo location</a>
        </div>
        <p id="location-feedback" class="location-feedback" role="status" aria-live="polite" aria-atomic="true">{% if has_location %}Distances are measured from the coordinates below.{% else %}Add a location for distance sorting, or browse by name and address.{% endif %}</p>
        <details data-manual-location{% if form.latitude.errors or form.longitude.errors or has_location or form.non_field_errors %} open{% endif %}>
          <summary>Enter or check coordinates</summary>
          <div class="manual-location-fields">
            {% for field in form %}{% if field.name == 'latitude' or field.name == 'longitude' %}
            <div class="field-wrapper"><label class="form-label" for="{{ field.id_for_label }}">{{ field.label }}</label>{{ field }}{% if field.errors %}<ul class="field-errors" id="{{ field.auto_id }}_error">{% for error in field.errors %}<li>{{ error }}</li>{% endfor %}</ul>{% endif %}</div>
            {% endif %}{% endfor %}
            <button type="submit" class="btn btn-outline-primary">Apply coordinates</button>
          </div>
          <p class="field-help">Demo centre: latitude 12.970000, longitude 77.590000. This is a synthetic test location, not your location. Text search matches stored names, addresses and specialities; it does not convert place names into coordinates.</p>
        </details>
        <p class="finder-privacy">Location is requested only when you tap the button. Search coordinates are sent to this server in the URL and may appear in browser history and server logs; they are not saved to your profile. The map provider receives requests for the area you view.</p>
      </div>
    </form>
    {% if not form.errors %}
    <div class="finder-results-heading" id="results-heading">
      <div><h2 id="results-title">{{ page_obj.paginator.count }} facilit{{ page_obj.paginator.count|pluralize:'y,ies' }} found</h2><p>{% if has_location %}Nearest first · Approximate straight-line distance, not travel time.{% else %}A–Z · Add a location to see the nearest facilities first.{% endif %}</p></div>
      <a class="finder-reset" href="#facility-map-heading">Go to map {% include 'partials/icon.html' with name='arrow-down' class_name='icon-sm' only %}</a>
    </div>
    <div class="finder-layout">
      <section class="facility-list" aria-labelledby="results-title">
        {% for match in page_obj %}{% include 'partials/facility_card.html' with match=match number=forloop.counter only %}{% empty %}
        <div class="finder-empty"><span class="action-icon">{% include 'partials/icon.html' with name='search' class_name='icon-lg' only %}</span><h3>No matches this time.</h3><p>Try a different type or speciality, widen the distance, or clear your filters. The FAKE samples are near the demo location.</p><a class="btn btn-outline-primary" href="{% url 'facilities:nearby' %}">Browse all facilities</a></div>
        {% endfor %}
        {% if page_obj.paginator.num_pages > 1 %}
        <nav class="finder-pagination" aria-label="Search result pages">
          {% if previous_query %}<a class="btn btn-outline-primary" href="{{ previous_query }}#results-heading">Previous</a>{% endif %}
          <span>Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
          {% if next_query %}<a class="btn btn-outline-primary" href="{{ next_query }}#results-heading">Next</a>{% endif %}
        </nav>
        {% endif %}
      </section>
      <section class="finder-map-panel" aria-labelledby="facility-map-heading">
        <div class="finder-map-heading"><h2 id="facility-map-heading">A view of your search</h2><p>Numbered pins match the cards on this page. FAKE pins are labelled Demo.</p></div>
        <div id="facility-map" class="facility-map" aria-label="Facility locations; the same information is available in the list"></div>
        <p id="map-feedback" class="map-feedback" role="status" aria-live="polite">Loading the map… The list remains available below or alongside it.</p>
        <noscript><p class="map-feedback">Enable JavaScript to see the map. All facility details are available in the list.</p></noscript>
        <div class="map-legend"><span><i class="legend-dot" aria-hidden="true"></i> Facility</span><span><i class="legend-dot legend-demo" aria-hidden="true"></i> FAKE sample</span><span><i class="legend-dot legend-origin" aria-hidden="true"></i> Search location</span></div>
        <p class="map-credit">Map data © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap contributors</a> · <a href="https://www.openstreetmap.org/fixthemap" target="_blank" rel="noopener">Report a map issue</a></p>
      </section>
    </div>
    {{ map_data|json_script:'facility-map-data' }}
    {% endif %}
  </div>
</section>
{% endblock %}
{% block extra_js %}
<script src="{% static 'vendor/leaflet/leaflet.js' %}" defer></script>
<script src="{% static 'js/location.js' %}" defer></script>
<script src="{% static 'js/facilities.js' %}" defer></script>
{% endblock %}
```

### `templates/partials/navbar.html`

Find Hospitals opens the directory and highlights the current section.

```html
<header class="site-header">
  <nav class="navbar navbar-expand-lg" aria-label="Main navigation">
    <div class="container">
      <a class="navbar-brand" href="{% url 'core:home' %}" aria-label="MEDTAP home">
        <span class="brand-mark">{% include 'partials/icon.html' with name='heart-pulse' only %}</span>
        <span class="brand-word">medtap<span class="brand-dot">.</span></span>
      </a>
      <span class="preview-label me-auto d-lg-none">Preview</span>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#main-navigation" aria-controls="main-navigation" aria-expanded="false" aria-label="Toggle navigation">
        {% include 'partials/icon.html' with name='list' class_name='icon-lg' only %}
      </button>
      <div class="collapse navbar-collapse" id="main-navigation">
        <ul class="navbar-nav">
          <li class="nav-item"><a class="nav-link{% if request.resolver_match.view_name == 'core:home' %} active{% endif %}" {% if request.resolver_match.view_name == 'core:home' %}aria-current="page"{% endif %} href="{% url 'core:home' %}">Home</a></li>
          <li class="nav-item"><a class="nav-link{% if request.resolver_match.namespace == 'facilities' %} active{% endif %}"{% if request.resolver_match.namespace == 'facilities' %} aria-current="page"{% endif %} href="{% url 'facilities:nearby' %}">Find Hospitals</a></li>
          <li class="nav-item"><button class="nav-link" type="button" data-bs-toggle="modal" data-bs-target="#feature-preview" data-preview-title="First-aid guides" data-preview-description="First-aid guides are not available in this preview. In a medical emergency, call 112 and follow the dispatcher's instructions.">First Aid</button></li>
          <li class="nav-item"><a class="nav-link" href="#emergency-numbers">Helplines</a></li>
        </ul>
        <div class="navbar-actions">
          {% if not user.is_authenticated %}<span class="preview-label d-none d-lg-inline">Project preview</span>{% endif %}
          {% if user.is_authenticated %}
          <a class="btn btn-outline-primary" href="{% url 'accounts:profile' %}">My profile</a>
          <form method="post" action="{% url 'accounts:logout' %}" class="logout-form">{% csrf_token %}<button class="btn btn-outline-primary" type="submit">Sign out</button></form>
          {% else %}
          <a class="btn btn-outline-primary" href="{% url 'accounts:login' %}">Login</a>
          {% endif %}
          <a class="btn btn-primary d-none d-lg-inline-flex" href="tel:112">
            {% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call 112
          </a>
        </div>
      </div>
    </div>
  </nav>
</header>
```

### `templates/partials/action_card.html`

Available search actions use helpful labels instead of Coming soon.

```html
{% if card.href %}
<a href="{{ card.href }}" class="action-card" aria-describedby="action-description-{{ card.key }}">
{% else %}
<button type="button" class="action-card" aria-describedby="action-description-{{ card.key }}" data-bs-toggle="modal" data-bs-target="#feature-preview" data-preview-title="{{ card.title }}" data-preview-description="{{ card.preview_description }}"{% if card.critical %} data-preview-critical="true"{% endif %}>
{% endif %}
  <span class="action-card-top">
    <span class="action-icon{% if card.tone == 'teal' %} action-icon-teal{% endif %}">{% include 'partials/icon.html' with name=card.icon class_name='icon-lg' only %}</span>
    <span class="action-arrow">{% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</span>
  </span>
  <span class="action-title">{{ card.title }}</span>
  <span class="action-description" id="action-description-{{ card.key }}">{{ card.description }}</span>
  <span class="action-status{% if card.available or card.status %} action-status-ready{% endif %}">{% if card.status %}{{ card.status }}{% elif card.available %}Call shortcut available{% else %}Coming soon{% endif %}</span>
{% if card.href %}</a>{% else %}</button>{% endif %}
```

### `templates/partials/footer.html`

The visible 112 disclaimer describes the remaining emergency previews.

```html
<footer class="site-footer">
  <div class="container">
    <div class="row g-4">
      <div class="col-lg-4">
        <a class="navbar-brand" href="{% url 'core:home' %}" aria-label="MEDTAP home">
          <span class="brand-mark">{% include 'partials/icon.html' with name='heart-pulse' only %}</span>
          <span class="brand-word">medtap<span class="brand-dot">.</span></span>
        </a>
        <p class="footer-description">A little closer to care.<br>A student project built around a clearer, calmer path to help.</p>
      </div>
      <div class="col-sm-4 col-lg-3" id="emergency-numbers">
        <p class="footer-label mb-1">India emergency helpline</p>
        <a class="footer-call" href="tel:112">{% include 'partials/icon.html' with name='telephone' only %} 112</a>
        <p class="text-muted small mb-0">For immediate emergency assistance.</p>
      </div>
      <div class="col-sm-8 col-lg-5">
        <p class="footer-label">Please remember</p>
        <p class="footer-disclaimer mb-0"><strong>This app does not replace calling 112.</strong> SOS sharing and ambulance booking are not available in this preview. No emergency contacts or transport providers are contacted.</p>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; {% now 'Y' %} MEDTAP. Built with care.</span>
      <span>Medical Emergency App &middot; Student project</span>
    </div>
  </div>
</footer>
```

### `templates/core/home.html`

The existing design now submits actual searches using the shared location script.

```html
{% extends 'base.html' %}
{% load static %}
{% block title %}MEDTAP | The right care, a little closer{% endblock %}
{% block content %}
<section class="hero-section" aria-labelledby="hero-heading">
  <div class="hero-shell">
    <div class="hero-grid">
      <div class="hero-copy">
        <p class="hero-kicker">{% include 'partials/icon.html' with name='heart-pulse' class_name='icon-sm' only %} Healthcare, with a human touch</p>
        <h1 class="hero-title" id="hero-heading">The right care.<br>A little <span>closer.</span></h1>
        <p class="hero-description">Find your way to nearby hospitals, essential resources, and the people you count on. A clearer next step, when it matters most.</p>
        <section class="search-panel" id="find-care" aria-labelledby="search-heading">
          <h2 id="search-heading">Find nearby hospitals</h2>
          <form action="{% url 'facilities:nearby' %}" method="get" id="care-search-form" data-location-form role="search" aria-label="Find facilities">
            <input type="hidden" name="latitude" value="">
            <input type="hidden" name="longitude" value="">
            <label class="visually-hidden" for="care-query">{{ search_form.q.label }}</label>
            <div class="search-controls">
              <div class="query-field">
                {% include 'partials/icon.html' with name='search' class_name='icon-sm' only %}
                {{ search_form.q }}
              </div>
              <button type="submit" class="btn btn-primary">Find care {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</button>
            </div>
            <div class="home-location-actions">{% include 'partials/location_button.html' %}<a href="{% url 'facilities:nearby' %}">Browse all facilities</a></div>
            <p class="search-hint" id="search-hint">Search listed names and addresses. For distance sorting, share your location or enter coordinates on the results page. Shared coordinates appear in the search URL and may appear in history and server logs.</p>
            <p class="location-feedback" id="location-feedback" role="status" aria-live="polite" aria-atomic="true"></p>
          </form>
          <noscript><p class="search-hint">The location button needs JavaScript. Name and address search still works.</p></noscript>
        </section>
        <div class="hero-details">
          <span>{% include 'partials/icon.html' with name='geo-alt' class_name='icon-sm' only %} Location shared with your permission</span>
          <span>{% include 'partials/icon.html' with name='phone' class_name='icon-sm' only %} Made for your phone</span>
        </div>
      </div>
      <figure class="hero-art">
        <img class="hero-photo" src="{% static 'img/care-professional-v2.png' %}" width="1122" height="1402" fetchpriority="high" alt="Illustrative portrait of a healthcare professional in blue scrubs in a bright hospital corridor.">
        <div class="hero-note">
          <span class="hero-note-icon">{% include 'partials/icon.html' with name='heart-pulse' only %}</span>
          <div><strong>People first.<br>Every step of the way.</strong><p>A clearer path to the care around you.</p></div>
        </div>
        <figcaption class="image-caption">AI-generated illustration &middot; Not a listed provider</figcaption>
      </figure>
    </div>
  </div>
</section>
<section class="emergency-section" aria-labelledby="urgent-heading">
  <div class="container">
    <div class="emergency-band">
      {% include 'partials/sos_button.html' with describedby='sos-preview-note' only %}
      <div class="emergency-copy">
        <h2 id="urgent-heading">When it's urgent, start here.</h2>
        <p id="sos-preview-note">Call 112 for immediate emergency help. SOS sharing and ambulance booking are previews only.</p>
      </div>
      <a href="tel:112" class="btn btn-primary">{% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call 112 directly {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</a>
    </div>
  </div>
</section>
<section class="quick-actions-section" id="quick-actions" aria-labelledby="quick-actions-heading">
  <div class="container">
    <div class="section-heading">
      <div><p class="eyebrow">Your care, connected</p><h2 id="quick-actions-heading">What do you need today?</h2></div>
      <p>Essential resources.<br>One place to start.</p>
    </div>
    <div class="care-grid">
      {% for card in quick_actions %}{% include 'partials/action_card.html' with card=card only %}{% endfor %}
    </div>
  </div>
</section>
<section class="how-section" aria-labelledby="how-heading">
  <div class="container">
    <div class="how-panel">
      <div class="how-intro">
        <p class="eyebrow">A calmer way forward</p>
        <h2 id="how-heading">For the moments<br>that matter.</h2>
        <p>Knowing where to start can make a difficult moment feel less overwhelming. We're building MEDTAP with that simple idea in mind.</p>
      </div>
      <div class="how-steps">
        <div class="simple-step"><span class="step-number" aria-hidden="true">01</span><div><h3>Call for urgent help</h3><p>Use the Call 112 shortcut to reach emergency services directly.</p></div></div>
        <div class="simple-step"><span class="step-number" aria-hidden="true">02</span><div><h3>Know what's around you</h3><p>Explore facilities on a map and compare approximate distances. FAKE samples are clearly marked.</p></div></div>
        <div class="simple-step"><span class="step-number" aria-hidden="true">03</span><div><h3>Keep your people close</h3><p>Save medical details and emergency contacts in your private account.</p><a class="back-link" href="{% if user.is_authenticated %}{% url 'accounts:profile' %}{% else %}{% url 'accounts:register' %}{% endif %}">{% if user.is_authenticated %}View your profile{% else %}Create your account{% endif %} {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</a></div></div>
      </div>
    </div>
  </div>
</section>
{% endblock %}
{% block extra_js %}<script src="{% static 'js/location.js' %}" defer></script>{% endblock %}
```

### `static/css/theme.css`

The complete current theme, including existing account styles and responsive finder styles.

```css
/* MEDTAP redesign: an original Django implementation inspired by Mediso on Framer. */
:root {
  --primary: #0077B6;
  --primary-dark: #023E8A;
  --accent: #2A9D8F;
  --emergency: #D62828;
  --bg: #F5F9FC;
  --text: #1F2933;
  --ink: #15333F;
  --muted: #526375;
  --accent-dark: #17665D;
  --surface: #FFFFFF;
  --hero-bg: #EDF5F6;
  --blue-soft: #EAF4FB;
  --teal-soft: #EAF6F3;
  --border: #D8E3E7;
  --radius: 1.5rem;
  --shadow: 0 16px 48px rgb(21 51 63 / 9%);
  --bs-body-font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
  --bs-body-font-size: 1rem;
  --bs-body-line-height: 1.65;
  --bs-body-color: var(--text);
  --bs-body-bg: var(--surface);
  --bs-link-color: var(--primary-dark);
  --bs-link-hover-color: var(--ink);
}
html { scroll-behavior: smooth; scroll-padding-top: 7rem; }
body { min-width: 320px; }
body, button, input, select, textarea { font-family: var(--bs-body-font-family); }
h1, h2, h3, h4 { color: var(--ink); font-weight: 500; line-height: 1.15; }
a { text-underline-offset: .2em; }
button, input, select, .btn { font-size: 1rem; }
button, .btn, .form-control, .form-select { min-height: 44px; }
[hidden] { display: none !important; }
:focus-visible { outline: 3px solid var(--primary-dark) !important; outline-offset: 4px; }
.form-control:focus { border-color: var(--primary-dark); box-shadow: 0 0 0 3px rgb(2 62 138 / 15%); }
.container { max-width: 1240px; }
.icon { display: inline-block; width: 1.25rem; height: 1.25rem; fill: currentColor; flex-shrink: 0; vertical-align: -.18em; }
.icon-sm { width: 1rem; height: 1rem; }
.icon-lg { width: 1.75rem; height: 1.75rem; }
.skip-link { position: fixed; top: -6rem; left: 1rem; z-index: 2000; padding: .8rem 1.2rem; border-radius: .6rem; background: var(--primary-dark); color: white; }
.skip-link:focus { top: 1rem; color: white; }
.text-muted { color: var(--muted) !important; }
.eyebrow { margin-bottom: .85rem; color: var(--accent-dark); font-size: .75rem; font-weight: 600; letter-spacing: .13em; text-transform: uppercase; }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: .6rem; border-radius: 999px; padding: .8rem 1.35rem; font-weight: 500; }
.btn-primary {
  --bs-btn-color: #fff;
  --bs-btn-bg: var(--primary-dark);
  --bs-btn-border-color: var(--primary-dark);
  --bs-btn-hover-color: #fff;
  --bs-btn-hover-bg: #032F67;
  --bs-btn-hover-border-color: #032F67;
  --bs-btn-active-color: #fff;
  --bs-btn-active-bg: #032F67;
  --bs-btn-active-border-color: #032F67;
}
.btn-outline-primary {
  --bs-btn-color: var(--primary-dark);
  --bs-btn-border-color: var(--border);
  --bs-btn-hover-color: var(--primary-dark);
  --bs-btn-hover-bg: var(--blue-soft);
  --bs-btn-hover-border-color: var(--primary-dark);
  --bs-btn-active-color: var(--primary-dark);
  --bs-btn-active-bg: var(--blue-soft);
  --bs-btn-active-border-color: var(--primary-dark);
}
.btn-emergency { background: var(--emergency); border: 1px solid var(--emergency); color: white; }
.btn-emergency:hover, .btn-emergency:active { background: #AF2020; border-color: #AF2020; color: white; }
.btn-close { box-sizing: border-box; width: 44px; height: 44px; min-width: 44px; min-height: 44px; background-size: .8rem; opacity: .8; }
.site-header { position: sticky; top: 0; z-index: 1020; background: rgb(255 255 255 / 98%); border-bottom: 1px solid #EAF0F2; }
.site-header .navbar { min-height: 94px; }
.navbar-brand { display: inline-flex; align-items: center; gap: .65rem; min-height: 44px; margin-right: 1.5rem; padding-block: .35rem; color: var(--ink); text-decoration: none; }
.brand-mark { display: inline-flex; align-items: center; justify-content: center; width: 39px; height: 39px; border-radius: 50%; color: white; background: var(--primary-dark); }
.brand-word { font-size: 1.65rem; font-weight: 700; line-height: 1.1; letter-spacing: -.065em; }
.brand-dot { color: var(--accent-dark); }
.preview-label { margin-left: .35rem; border: 1px solid var(--border); border-radius: 999px; padding: .15rem .5rem; color: var(--muted); font-size: .65rem; font-weight: 500; letter-spacing: .02em; }
.navbar .nav-link { display: inline-flex; align-items: center; min-height: 44px; padding: .6rem .85rem !important; color: var(--muted); font-size: .88rem; font-weight: 500; background: none; border: 0; border-radius: 999px; text-decoration: none; }
.navbar .nav-link:hover, .navbar .nav-link.active { color: var(--primary-dark); }
.navbar .nav-link.active::after { content: ""; width: 4px; height: 4px; border-radius: 50%; background: var(--primary-dark); margin-left: .4rem; }
.navbar-toggler { min-width: 44px; border-color: var(--border); color: var(--ink); border-radius: 50%; }
.navbar-actions { display: flex; align-items: center; gap: .6rem; }
.navbar-actions .btn { font-size: .85rem; padding: .65rem 1.15rem; }
.site-main { min-height: 50vh; }
.message-container { padding-top: 1.25rem; }
.alert { border-radius: .8rem; }
.alert-danger { color: #831818; background: #FFF1F1; border-color: #EAB4B4; }
.alert-info { color: var(--primary-dark); background: var(--blue-soft); border-color: var(--border); }
.alert-success { color: var(--accent-dark); background: var(--teal-soft); border-color: #B8DCD3; }
.hero-section { padding: 1.5rem 1.5rem 0; }
.hero-shell { max-width: 1360px; margin: auto; padding: 3rem; border-radius: 1.8rem; background: var(--hero-bg); }
.hero-grid { display: grid; grid-template-columns: 1.1fr 1fr; gap: 3.25rem; align-items: center; }
.hero-copy { min-width: 0; }
.hero-kicker { display: inline-flex; align-items: center; gap: .55rem; padding: .4rem .8rem; margin-bottom: 1.4rem; border: 1px solid #C8DAD8; border-radius: 999px; color: var(--accent-dark); background: #F6FBF9; font-size: .75rem; font-weight: 500; }
.hero-title { margin: 0 0 1.4rem; font-size: clamp(2.75rem, 4.8vw, 4.5rem); font-weight: 500; letter-spacing: -.07em; line-height: 1.04; }
.hero-title span { color: var(--primary-dark); }
.hero-description { max-width: 29rem; margin-bottom: 1.8rem; font-size: 1rem; color: var(--muted); line-height: 1.75; }
.hero-art { position: relative; margin: 0; min-width: 0; padding-bottom: .9rem; }
.hero-photo { display: block; width: 100%; height: 560px; object-fit: cover; object-position: 50% 35%; border-radius: 1.25rem; background: #DCE9EC; }
.hero-note { position: absolute; left: -1.3rem; bottom: 3.1rem; display: flex; align-items: center; gap: .85rem; width: min(310px, 90%); padding: 1.1rem; border: 1px solid rgb(255 255 255 / 80%); border-radius: 1rem; box-shadow: var(--shadow); background: white; }
.hero-note-icon { display: flex; align-items: center; justify-content: center; flex-shrink: 0; width: 46px; height: 46px; border-radius: .85rem; color: var(--primary-dark); background: var(--blue-soft); }
.hero-note strong { display: block; font-size: .9rem; font-weight: 600; line-height: 1.4; color: var(--ink); }
.hero-note p { margin: .25rem 0 0; color: var(--muted); font-size: .75rem; line-height: 1.5; }
.image-caption { position: absolute; right: .2rem; bottom: -.65rem; margin: 0; color: var(--muted); font-size: .65rem; }
.search-panel { padding: 1.2rem; border: 1px solid #D5E2E4; border-radius: 1.1rem; background: var(--surface); box-shadow: 0 6px 18px rgb(21 51 63 / 3%); }
.search-panel h2 { font-size: 1rem; font-weight: 600; margin: 0 0 .8rem; letter-spacing: -.02em; }
.search-controls { display: flex; align-items: stretch; gap: .55rem; }
.query-field { display: flex; align-items: center; flex: 1; min-width: 0; gap: .25rem; border: 1px solid #7A9099; border-radius: 999px; padding-left: .8rem; color: var(--muted); background: #FAFCFC; }
.query-field:focus-within { border-color: var(--primary-dark); box-shadow: 0 0 0 2px rgb(2 62 138 / 15%); }
.query-field .form-control { min-width: 0; min-height: 50px; padding: .65rem .65rem .65rem .3rem; border: 0; border-radius: 999px; background: transparent; color: var(--text); font-size: 1rem; box-shadow: none; }
.query-field .form-control:focus-visible { outline-offset: 0; }
.query-field .form-control::placeholder { color: var(--muted); opacity: 1; font-size: .85rem; }
.search-controls .btn { padding-inline: 1rem; font-size: .85rem; white-space: nowrap; }
.location-button { display: inline-flex; align-items: center; gap: .45rem; margin-top: .4rem; padding: .4rem 0; min-height: 44px; color: var(--primary-dark); border: 0; background: transparent; font-size: .8rem; text-align: left; }
.location-button:hover { text-decoration: underline; text-underline-offset: .2em; }
.location-button:disabled { opacity: .8; }
.search-hint { margin: .1rem 0 0; color: var(--muted); font-size: .73rem; line-height: 1.6; }
.location-feedback { margin: .6rem 0 0; color: var(--primary-dark); font-size: .85rem; }
.location-feedback:empty { display: none; }
.search-feedback { margin-top: .8rem; padding: .85rem; border: 1px solid var(--border); border-radius: .7rem; color: var(--primary-dark); background: var(--blue-soft); font-size: .9rem; }
.form-errors { color: var(--primary-dark); font-size: .9rem; }
.hero-details { display: flex; align-items: center; flex-wrap: wrap; gap: .75rem 1rem; color: var(--muted); font-size: .73rem; margin-top: 1.1rem; }
.hero-details span { display: inline-flex; align-items: center; gap: .4rem; }
.hero-details .icon { color: var(--accent-dark); }
.emergency-section { padding: 1.5rem 0 0; }
.emergency-band { display: flex; align-items: center; gap: 1.5rem; border: 1px solid #E9D4D1; border-radius: 1.25rem; padding: 1.3rem 1.6rem; background: #FFFAF9; }
.sos-button { display: flex; flex-shrink: 0; flex-direction: column; justify-content: center; align-items: center; gap: 0; width: 88px; height: 88px; min-height: 88px; padding: 0; color: white; background: var(--emergency); border: 5px solid white; border-radius: 50%; animation: sos-pulse 3.2s ease-out infinite; }
.sos-button:hover { color: white; background: #AF2020; }
.sos-button strong { font-size: 1.45rem; font-weight: 700; line-height: 1.2; letter-spacing: .03em; }
.sos-button span { font-size: .65rem; }
.emergency-copy { flex: 1; min-width: 0; }
.emergency-copy h2 { font-size: 1.3rem; letter-spacing: -.035em; margin: 0 0 .35rem; }
.emergency-copy p { margin: 0; max-width: 41rem; color: var(--muted); font-size: 1rem; }
.emergency-band > .btn { flex-shrink: 0; }
.quick-actions-section { padding: 5.5rem 0; }
.section-heading { display: flex; align-items: end; justify-content: space-between; gap: 2rem; margin-bottom: 2rem; }
.section-heading h2 { margin: 0; font-size: clamp(2rem, 3.1vw, 2.75rem); letter-spacing: -.055em; }
.section-heading > p { max-width: 17rem; margin: 0 0 .2rem; color: var(--muted); font-size: 1rem; }
.care-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }
.action-card { display: flex; flex-direction: column; align-items: flex-start; width: 100%; height: 100%; min-width: 0; min-height: 225px; padding: 1.7rem; border: 1px solid var(--border); border-radius: 1.1rem; background: white; color: var(--text); text-align: left; text-decoration: none; transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease; }
.action-card:hover { color: var(--text); border-color: #99BEC6; box-shadow: 0 10px 30px rgb(21 51 63 / 6%); transform: translateY(-3px); }
.action-card-top { display: flex; align-items: center; justify-content: space-between; width: 100%; margin-bottom: 1.6rem; }
.action-icon { display: inline-flex; align-items: center; justify-content: center; width: 50px; height: 50px; color: var(--primary-dark); background: var(--blue-soft); border-radius: 50%; }
.action-icon-teal { color: var(--accent-dark); background: var(--teal-soft); }
.action-arrow { display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; color: var(--ink); border: 1px solid var(--border); border-radius: 50%; }
.action-title { font-size: 1.2rem; line-height: 1.3; font-weight: 500; letter-spacing: -.03em; color: var(--ink); }
.action-description { display: block; margin-top: .55rem; font-size: 1rem; line-height: 1.6; color: var(--muted); }
.action-status { display: inline-flex; align-items: center; gap: .4rem; font-size: .7rem; color: var(--muted); margin-top: 1rem; }
.action-status::before { content: ""; width: 5px; height: 5px; border-radius: 50%; background: #7A8B95; }
.action-status-ready { color: var(--accent-dark); }
.action-status-ready::before { background: var(--accent-dark); }
.how-section { padding: 0 0 5.5rem; }
.how-panel { display: grid; grid-template-columns: 1fr 1.15fr; gap: 4rem; padding: 3rem; border-radius: 1.5rem; background: var(--hero-bg); }
.how-intro h2 { font-size: clamp(2rem, 3vw, 2.65rem); letter-spacing: -.055em; }
.how-intro > p:last-child { max-width: 24rem; margin: 1rem 0 0; color: var(--muted); font-size: 1rem; }
.simple-step { display: flex; align-items: start; gap: 1.1rem; padding: 1.15rem 0; border-bottom: 1px solid #CEDFE2; }
.simple-step:first-child { padding-top: .25rem; }
.simple-step:last-child { border-bottom: 0; padding-bottom: 0; }
.step-number { color: var(--accent-dark); font-size: .8rem; line-height: 1.6; padding-top: .15rem; }
.simple-step h3 { font-size: 1.05rem; font-weight: 500; margin: 0 0 .35rem; }
.simple-step p { font-size: 1rem; color: var(--muted); margin: 0; }
.site-footer { background: #102F40; color: white; padding: 3.5rem 0 1.4rem; }
.site-footer .navbar-brand { color: white; }
.site-footer .brand-mark { background: white; color: #102F40; }
.site-footer .brand-dot { color: #9ED4C5; }
.footer-description { max-width: 23rem; margin-top: 1.2rem; color: #C0D2DF; font-size: .9rem; }
.footer-label { color: #C0D2DF; font-size: .72rem; font-weight: 500; letter-spacing: .1em; text-transform: uppercase; margin-bottom: .8rem; }
.footer-call { display: inline-flex; align-items: center; gap: .75rem; min-height: 44px; color: white; font-size: 2.8rem; font-weight: 500; letter-spacing: -.04em; text-decoration: none; }
.footer-call:hover { color: #C9E6F5; }
.site-footer .text-muted { color: #C0D2DF !important; }
.site-footer :focus-visible { outline-color: white !important; }
.footer-disclaimer { max-width: 30rem; color: #E2ECF1; font-size: 1rem; }
.footer-disclaimer strong { display: block; color: white; font-weight: 500; margin-bottom: .6rem; }
.footer-bottom { display: flex; justify-content: space-between; flex-wrap: wrap; gap: .75rem; margin-top: 2.5rem; padding-top: 1.2rem; border-top: 1px solid #3A5361; color: #C0D2DF; font-size: .75rem; }
.mobile-emergency-bar { display: none; }
.modal-content { border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow); }
.modal-header { padding: 1.2rem 1.4rem; border-color: var(--border); }
.modal-title { font-size: 1.2rem; font-weight: 500; }
.modal-body, .modal-footer { padding: 1.2rem 1.4rem; }
.modal-footer { border-color: var(--border); }
.critical-note { padding: .85rem; border-left: 3px solid var(--emergency); border-radius: .3rem; color: #831818; background: #FFF1F1; }
@keyframes sos-pulse {
  0%, 75%, 100% { box-shadow: 0 0 0 1px #E5C1BC, 0 0 0 6px rgb(214 40 40 / 4%); }
  40% { box-shadow: 0 0 0 1px #E5C1BC, 0 0 0 13px rgb(214 40 40 / 0%); }
}
@media (min-width: 992px) {
  .navbar-collapse { justify-content: flex-end; gap: 1.5rem; }
  .navbar-nav { gap: .15rem; }
}
@media (max-width: 1199.98px) {
  .hero-shell { padding: 2rem; }
  .hero-grid { gap: 2rem; }
  .hero-photo { height: 530px; }
  .hero-title { font-size: 3.5rem; }
  .navbar .nav-link { padding-inline: .65rem !important; }
  .navbar-collapse { gap: .7rem; }
}
@media (max-width: 991.98px) {
  body { padding-bottom: calc(82px + env(safe-area-inset-bottom)); }
  .site-header .navbar { min-height: 78px; }
  .navbar-collapse { padding-block: .75rem; }
  .navbar .nav-link { width: 100%; padding-inline: .85rem !important; }
  .navbar-actions { padding-top: .75rem; }
  .hero-grid { grid-template-columns: 1fr 1fr; gap: 1.5rem; }
  .hero-shell { padding: 2rem; }
  .hero-title { font-size: 2.8rem; }
  .hero-photo { height: 520px; }
  .hero-description { font-size: 1rem; }
  .search-controls { flex-direction: column; }
  .search-controls > .btn { min-height: 46px; }
  .hero-note { left: -.75rem; bottom: 3rem; padding: .8rem; gap: .6rem; }
  .hero-note-icon { width: 38px; height: 38px; }
  .hero-note strong { font-size: .8rem; }
  .hero-note p { font-size: .7rem; }
  .emergency-band { flex-wrap: wrap; gap: 1.2rem; }
  .emergency-copy { flex-basis: calc(100% - 110px); }
  .emergency-band > .btn:not(.sos-button) { margin-left: 110px; }
  .quick-actions-section { padding-block: 4rem; }
  .care-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .how-panel { gap: 2rem; padding: 2rem; }
  .how-section { padding-bottom: 4rem; }
  .mobile-emergency-bar { position: fixed; display: flex; justify-content: space-between; align-items: center; gap: .75rem; left: 0; right: 0; bottom: 0; z-index: 1030; padding: .6rem 1.25rem calc(.6rem + env(safe-area-inset-bottom)); border-top: 1px solid var(--border); background: white; box-shadow: 0 -4px 18px rgb(21 51 63 / 6%); }
  .mobile-emergency-bar p { font-size: .75rem; color: var(--muted); margin: 0; line-height: 1.4; }
  .mobile-emergency-bar strong { display: block; color: var(--text); font-weight: 600; }
  .mobile-bar-actions { display: flex; align-items: center; gap: .6rem; }
  .mobile-bar-actions > .btn { padding: .7rem 1rem; font-size: .85rem; }
  .sos-button-compact { min-height: 48px; height: 48px; width: 48px; border: 0; animation: none; }
  .sos-button-compact strong { font-size: .85rem; }
  .sos-button-compact span { font-size: .5rem; }
}
@media (max-width: 767.98px) {
  .hero-section { padding: .75rem .75rem 0; }
  .hero-shell { padding: 2rem 1.5rem 1.5rem; }
  .hero-grid { grid-template-columns: 1fr; gap: 1.75rem; }
  .hero-title { font-size: clamp(2.75rem, 8vw, 3.8rem); }
  .hero-description { max-width: 31rem; }
  .search-controls { flex-direction: row; }
  .hero-photo { height: 350px; object-position: 50% 32%; }
  .hero-note { left: .8rem; bottom: 2.5rem; width: 280px; }
  .hero-note strong { font-size: .85rem; }
  .hero-art { padding-bottom: 1.1rem; }
  .image-caption { right: .1rem; bottom: -.1rem; }
  .section-heading { flex-direction: column; align-items: start; gap: 1rem; }
  .section-heading > p { max-width: none; }
  .how-panel { grid-template-columns: 1fr; gap: 1.75rem; }
}
@media (max-width: 575.98px) {
  .container { padding-inline: 1.25rem; }
  .site-header .navbar { min-height: 74px; }
  .brand-word { font-size: 1.5rem; }
  .brand-mark { width: 36px; height: 36px; }
  .preview-label { font-size: .6rem; }
  .hero-shell { border-radius: 1.25rem; padding: 1.6rem 1.15rem 1.25rem; }
  .hero-kicker { margin-bottom: 1.2rem; font-size: .7rem; }
  .hero-title { font-size: clamp(2.6rem, 10.5vw, 3.5rem); margin-bottom: 1.1rem; }
  .hero-description { margin-bottom: 1.4rem; }
  .search-panel { padding: 1rem; }
  .search-controls { flex-direction: column; }
  .hero-photo { height: 300px; border-radius: 1rem; }
  .hero-note { width: 245px; max-width: calc(100% - 1.6rem); }
  .hero-details { gap: .55rem; font-size: .7rem; }
  .emergency-section { padding-top: 1.1rem; }
  .emergency-band { padding: 1.2rem; gap: 1rem; }
  .emergency-copy { flex-basis: calc(100% - 92px); }
  .emergency-copy h2 { font-size: 1.1rem; }
  .emergency-copy p { font-size: .9rem; }
  .emergency-band > .sos-button { width: 72px; height: 72px; min-height: 72px; }
  .emergency-band > .sos-button strong { font-size: 1.2rem; }
  .emergency-band > .btn:not(.sos-button) { margin-left: 0; width: 100%; }
  .quick-actions-section { padding-block: 3rem; }
  .section-heading { margin-bottom: 1.5rem; }
  .care-grid { gap: .65rem; }
  .action-card { padding: 1rem; min-height: 235px; border-radius: .85rem; }
  .action-card-top { margin-bottom: 1.2rem; }
  .action-icon { width: 42px; height: 42px; }
  .action-arrow { width: 27px; height: 27px; }
  .action-arrow .icon { width: .8rem; height: .8rem; }
  .action-title { font-size: 1rem; }
  .action-description { font-size: 1rem; line-height: 1.5; }
  .action-status { font-size: .65rem; }
  .how-panel { padding: 1.5rem; border-radius: 1.1rem; }
  .how-section { padding-bottom: 3rem; }
  .site-footer { padding-top: 2.5rem; }
  .footer-bottom { margin-top: 1.5rem; }
  .mobile-emergency-bar { padding-inline: 1rem; }
  .mobile-emergency-bar p { font-size: .65rem; }
  .mobile-bar-actions { gap: .45rem; }
}
/* Accounts: shared forms and a private medical ID, using the existing theme. */
.account-section { padding: 3rem 0 4.5rem; }
.auth-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; align-items: start; }
.auth-intro { padding: 2.7rem; border-radius: var(--radius); background: var(--hero-bg); }
.auth-intro h1 { font-size: clamp(2rem, 3.2vw, 3rem); letter-spacing: -.055em; margin-bottom: 1.4rem; }
.auth-intro > p { font-size: 1rem; color: var(--muted); }
.auth-intro > .eyebrow { color: var(--accent-dark); font-size: .75rem; }
.auth-benefits { display: grid; gap: 1.2rem; margin-top: 2rem; }
.auth-benefits > div { display: flex; align-items: start; gap: .8rem; color: var(--muted); font-size: 1rem; }
.auth-benefits .icon { margin-top: .2rem; color: var(--accent-dark); }
.auth-intro .auth-reminder { border-top: 1px solid #CADCE0; padding-top: 1.3rem; margin: 2rem 0 0; }
.account-panel { padding: 2rem; min-width: 0; border: 1px solid var(--border); border-radius: 1.2rem; background: white; }
.account-panel > h1 { font-size: clamp(1.8rem, 3vw, 2.4rem); letter-spacing: -.045em; }
.account-panel > h2, .panel-title-row > h2 { font-size: 1.5rem; letter-spacing: -.035em; margin-bottom: 1rem; }
.field-wrapper { margin-bottom: 1.35rem; min-width: 0; }
.field-wrapper .form-label { display: block; font-weight: 500; font-size: .9rem; margin-bottom: .5rem; }
.field-wrapper .form-control, .field-wrapper .form-select { min-height: 48px; padding: .7rem .85rem; border: 1px solid #7A9099; border-radius: .6rem; background-color: #FCFDFD; font-size: 1rem; }
.field-wrapper textarea.form-control { resize: vertical; }
.field-wrapper [aria-invalid='true'] { border: 2px solid var(--primary-dark); }
.field-help { margin-top: .45rem; color: var(--muted); font-size: .8rem; line-height: 1.6; }
.field-help ul { margin: .25rem 0 0; padding-left: 1.2rem; }
.field-errors { margin: .45rem 0 0; padding-left: 1.2rem; color: var(--primary-dark); font-size: .9rem; }
.required-marker { color: var(--primary-dark); }
.optional-label { color: var(--muted); font-weight: 400; font-size: .8rem; }
.checkbox-label { display: flex; min-height: 44px; align-items: center; gap: .8rem; cursor: pointer; }
.checkbox-label .form-check-input { width: 1.2rem; height: 1.2rem; margin: 0; float: none; flex-shrink: 0; border-color: #6B818A; }
.checkbox-label .form-check-input:checked { background-color: var(--primary-dark); border-color: var(--primary-dark); }
.form-error-summary { padding: 1rem 1.2rem; margin-bottom: 1.5rem; border: 2px solid var(--primary-dark); border-radius: .7rem; background: var(--blue-soft); color: var(--primary-dark); }
.form-error-summary h2 { font-size: 1.1rem; font-weight: 600; margin-bottom: .5rem; }
.form-error-summary ul { margin: .4rem 0; padding-left: 1.2rem; }
.form-error-summary a { display: flex; align-items: center; min-height: 44px; color: var(--primary-dark); font-size: .9rem; }
.auth-switch { margin: 1.4rem 0 0; font-size: .9rem; color: var(--muted); }
.auth-switch a { display: inline-flex; align-items: center; min-height: 44px; font-weight: 500; }
.account-form-shell { max-width: 740px; margin: 0 auto; }
.back-link { display: inline-flex; align-items: center; gap: .5rem; min-height: 44px; margin-bottom: .8rem; color: var(--primary-dark); font-size: .9rem; }
.account-form-actions { display: flex; flex-wrap: wrap; align-items: center; gap: .75rem; margin-top: 1.6rem; }
.profile-page-heading { display: flex; align-items: end; justify-content: space-between; flex-wrap: wrap; gap: 1.5rem; margin-bottom: 2rem; }
.profile-page-heading h1 { font-size: clamp(2rem, 3.5vw, 3rem); letter-spacing: -.055em; }
.profile-layout { display: grid; grid-template-columns: .9fr 1.3fr; gap: 2rem; align-items: start; }
.medical-id { background: var(--hero-bg); border: 1px solid #C6D9DB; border-radius: 1.4rem; padding: 2rem; overflow-wrap: anywhere; }
.medical-id-top { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 1rem; align-items: center; margin-bottom: 2rem; }
.medical-id-top > span:first-child { color: var(--primary-dark); font-weight: 600; display: inline-flex; gap: .5rem; align-items: center; font-size: .85rem; }
.privacy-label { display: inline-flex; align-items: center; gap: .35rem; color: var(--accent-dark); font-size: .7rem; }
.medical-id h2 { font-size: 1.8rem; letter-spacing: -.045em; margin-bottom: .25rem; }
.medical-id-username { font-size: .85rem; color: var(--muted); }
.blood-group-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; padding-block: 1.2rem; margin-top: 1.8rem; border-block: 1px solid #C6D9DB; }
.medical-id-label { font-size: .8rem; color: var(--muted); margin-bottom: .35rem; }
.blood-group-value { font-size: 2rem; font-weight: 500; color: var(--primary-dark); margin: 0; line-height: 1.3; }
.self-reported, .primary-label { display: inline-flex; font-size: .7rem; padding: .25rem .6rem; border-radius: 999px; color: var(--accent-dark); background: #F5FCF9; border: 1px solid #B7D2C9; }
.medical-id-caption { font-size: .8rem; color: var(--muted); margin: 1.2rem 0 0; }
.profile-privacy-note { margin: 1.1rem .3rem 0; color: var(--muted); font-size: .8rem; }
.profile-details { display: grid; gap: 1.5rem; min-width: 0; }
.medical-detail { padding-block: 1.1rem; border-bottom: 1px solid var(--border); }
.medical-detail h3 { font-size: .85rem; color: var(--muted); font-weight: 500; }
.medical-detail p { margin-bottom: 0; font-size: 1rem; overflow-wrap: anywhere; }
.panel-title-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: .75rem; margin-bottom: .5rem; }
.panel-title-row > h2 { margin: 0; }
.panel-title-row > .btn { font-size: .8rem; padding-inline: .9rem; }
.contact-item { padding-top: 1.5rem; margin-top: 1.5rem; border-top: 1px solid var(--border); overflow-wrap: anywhere; }
.contact-heading { display: flex; flex-wrap: wrap; align-items: center; gap: .6rem; }
.contact-heading h3 { font-size: 1.1rem; font-weight: 500; margin: 0; }
.contact-relationship { color: var(--muted); font-size: .85rem; margin: .3rem 0; }
.contact-phone { margin-bottom: .75rem; font-size: 1rem; }
.contact-actions { display: flex; flex-wrap: wrap; gap: .5rem; }
.contact-actions .btn { font-size: .8rem; padding: .6rem .9rem; }
.empty-contacts { padding: 2rem 0 .5rem; }
.empty-contacts h3 { font-size: 1.2rem; margin-top: 1rem; }
.empty-contacts p { color: var(--muted); font-size: 1rem; margin-bottom: 0; }
.logout-form { margin: 0; }
.navbar-actions { flex-wrap: wrap; }
@media (max-width: 991.98px) {
  .auth-layout { gap: 1.5rem; }
  .auth-intro, .account-panel { padding: 1.5rem; }
  .profile-layout { grid-template-columns: 1fr 1.3fr; gap: 1.3rem; }
  .medical-id { padding: 1.5rem; }
}
@media (max-width: 767.98px) {
  .account-section { padding: 1.75rem 0 3rem; }
  .auth-layout, .profile-layout { grid-template-columns: 1fr; }
  .auth-benefits { display: none; }
  .auth-intro h1 { font-size: 2rem; }
  .auth-intro .auth-reminder { margin-top: 1rem; padding-top: 1rem; }
  .profile-page-heading { align-items: start; }
}
/* Facility finder: one filter form, an accessible card list and a companion map. */
.home-location-actions { display: flex; flex-wrap: wrap; align-items: center; gap: .75rem; margin-top: .85rem; }
.home-location-actions .btn { font-size: .85rem; padding: .6rem .9rem; }
.home-location-actions > a { display: inline-flex; min-height: 44px; align-items: center; font-size: .85rem; }
.finder-section { padding: 3rem 0 4rem; background: linear-gradient(var(--hero-bg), white 440px); }
.finder-heading { display: flex; justify-content: space-between; align-items: end; flex-wrap: wrap; gap: 1.5rem; margin-bottom: 2rem; }
.finder-heading h1 { font-size: clamp(2.25rem, 4vw, 3.5rem); letter-spacing: -.055em; }
.finder-heading p:last-child { max-width: 34rem; margin-bottom: 0; color: var(--muted); }
.finder-notice { display: flex; align-items: start; gap: .8rem; padding: 1rem 1.2rem; margin-bottom: 1.5rem; background: #F8FCFE; color: var(--primary-dark); border: 1px solid #BDD4E2; border-radius: 1rem; }
.finder-notice .icon { margin-top: .2rem; }
.finder-notice p { margin: 0; font-size: .9rem; }
.finder-filter-panel { padding: 1.5rem; background: white; border: 1px solid var(--border); border-radius: 1.25rem; box-shadow: 0 8px 28px rgb(21 51 63 / 5%); }
.finder-filters { display: grid; grid-template-columns: 1.5fr 1fr 1fr .8fr; gap: 1rem; }
.finder-filters .field-wrapper { margin-bottom: .8rem; }
.finder-filter-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 1rem; }
.finder-filter-actions > .btn { margin-left: auto; }
.finder-reset { display: inline-flex; align-items: center; gap: .4rem; min-height: 44px; font-size: .9rem; }
.finder-location { border-top: 1px solid var(--border); margin-top: 1.3rem; padding-top: 1.3rem; }
.finder-location-actions { display: flex; flex-wrap: wrap; gap: .6rem; }
.finder-location-actions .btn { font-size: .9rem; }
.finder-location .location-feedback { margin: .8rem 0; }
.finder-location details { margin-top: .5rem; }
.finder-location summary { display: list-item; min-height: 44px; padding-block: .5rem; color: var(--primary-dark); cursor: pointer; font-weight: 500; }
.manual-location-fields { display: grid; grid-template-columns: 1fr 1fr auto; align-items: end; gap: 1rem; margin-top: .5rem; }
.manual-location-fields .field-wrapper { margin-bottom: 0; }
.manual-location-fields .btn { min-height: 48px; }
.finder-privacy { color: var(--muted); font-size: .85rem; max-width: 68rem; margin: .8rem 0 0; }
.finder-results-heading { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: .5rem; margin: 2.5rem 0 1.2rem; scroll-margin-top: 8rem; }
.finder-results-heading h2 { font-size: 1.6rem; letter-spacing: -.035em; }
.finder-results-heading p { color: var(--muted); font-size: .9rem; margin: 0; }
.finder-layout { display: grid; grid-template-columns: 1.05fr 1fr; gap: 1.5rem; align-items: start; }
.facility-list { display: grid; gap: 1rem; min-width: 0; }
.facility-card { border: 1px solid var(--border); border-radius: 1.1rem; padding: 1.4rem; background: white; scroll-margin-top: 8rem; overflow-wrap: anywhere; transition: box-shadow .18s ease, transform .18s ease; }
.facility-card:hover { box-shadow: var(--shadow); transform: translateY(-2px); }
.facility-card:target { border-color: var(--primary-dark); }
.facility-card-top { display: flex; align-items: center; flex-wrap: wrap; gap: .5rem; margin-bottom: .9rem; }
.facility-number { display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 50%; background: var(--primary-dark); color: white; font-size: .8rem; }
.facility-type, .facility-demo-label, .facility-hours { display: inline-flex; padding: .25rem .55rem; border-radius: 999px; font-size: .75rem; font-weight: 500; }
.facility-type { background: var(--blue-soft); color: var(--primary-dark); }
.facility-demo-label { background: #F1F3F5; color: #46515D; border: 1px dashed #65727F; }
.facility-card h3 { font-size: 1.4rem; letter-spacing: -.035em; line-height: 1.3; }
.facility-meta { display: flex; flex-wrap: wrap; align-items: center; gap: .65rem; color: var(--muted); font-size: .85rem; margin: .8rem 0; }
.facility-hours { background: var(--teal-soft); color: var(--accent-dark); }
.facility-address { font-size: 1rem; color: var(--muted); }
.facility-specialities { list-style: none; display: flex; flex-wrap: wrap; gap: .4rem; padding: 0; margin-bottom: 1rem; }
.facility-specialities li { border: 1px solid var(--border); border-radius: .4rem; padding: .2rem .5rem; font-size: .75rem; color: var(--muted); }
.facility-demo-note { font-size: .85rem; color: var(--muted); padding: .6rem .8rem; background: var(--bg); border-radius: .5rem; }
.facility-card-actions { display: flex; flex-wrap: wrap; gap: .5rem; }
.facility-card-actions .btn { font-size: .85rem; padding: .6rem .85rem; }
.facility-card-actions .btn:disabled { opacity: 1; color: #5B6877; background: #F1F3F5; border-color: #D8E3E7; cursor: default; }
.facility-map-button { min-height: 44px; border: 0; background: transparent; color: var(--primary-dark); text-decoration: underline; text-underline-offset: .2em; font-size: .85rem; padding: .5rem .75rem; }
.finder-empty { padding: 2.5rem 1.5rem; background: var(--bg); border-radius: 1.1rem; }
.finder-empty h3 { margin-top: 1.4rem; font-size: 1.5rem; }
.finder-empty p { color: var(--muted); }
.finder-pagination { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: .8rem; padding-top: .75rem; }
.finder-pagination span { color: var(--muted); font-size: .9rem; }
.finder-map-panel { position: sticky; top: 115px; min-width: 0; border: 1px solid var(--border); border-radius: 1.1rem; background: var(--bg); overflow: hidden; }
.finder-map-heading { padding: 1.2rem 1.2rem .5rem; }
.finder-map-heading h2 { font-size: 1.2rem; letter-spacing: -.025em; }
.finder-map-heading p { color: var(--muted); font-size: .85rem; }
.facility-map { height: 430px; width: 100%; background: #E5ECEE; z-index: 0; font-family: var(--bs-body-font-family); }
.map-feedback, .map-credit { margin: 0; padding: .8rem 1.2rem; color: var(--muted); font-size: .85rem; }
.map-credit { padding-top: .2rem; }
.map-credit a, .map-card-link { display: inline-flex; min-height: 44px; align-items: center; }
.map-legend { display: flex; flex-wrap: wrap; gap: .7rem; padding: 0 1.2rem; color: var(--muted); font-size: .75rem; }
.map-legend > span { display: inline-flex; align-items: center; gap: .4rem; }
.legend-dot { display: inline-block; width: 12px; height: 12px; background: var(--primary-dark); border-radius: 50%; }
.legend-demo { background: #46515D; }
.legend-origin { background: var(--accent-dark); }
.facility-pin { display: flex !important; flex-direction: column; justify-content: center; align-items: center; border-radius: 50% 50% 50% 0; transform-origin: center; background: var(--primary-dark); color: white; border: 2px solid white; box-shadow: 0 2px 8px rgb(0 0 0 / 25%); }
.facility-pin span { font-weight: 700; font-size: 1rem; line-height: 1; }
.facility-pin small { font-size: .65rem; line-height: 1; margin-top: .25rem; }
.facility-pin-demo { background: #46515D; border-style: dashed; }
.search-location-pin { display: flex !important; align-items: center; justify-content: center; border: 3px solid white; border-radius: 50%; background: var(--accent-dark); color: white; font-size: 1.8rem; box-shadow: 0 2px 8px rgb(0 0 0 / 25%); }
.finder-map-panel .leaflet-control-zoom a { width: 44px; height: 44px; line-height: 44px; }
.finder-map-panel .leaflet-popup-content { font-size: .9rem; line-height: 1.6; }
.finder-map-panel .leaflet-popup-close-button { width: 44px; height: 44px; line-height: 44px; }
.finder-map-panel .leaflet-popup-content-wrapper { padding-right: 1rem; }
.finder-map-panel .leaflet-control-attribution { max-width: 100%; font-size: .7rem; }
@media (max-width: 991.98px) {
  .finder-filters { grid-template-columns: 1fr 1fr; }
  .finder-map-panel { top: 95px; }
  .facility-map { height: 380px; }
}
@media (max-width: 767.98px) {
  .finder-section { padding-top: 1.75rem; }
  .finder-layout { grid-template-columns: 1fr; }
  .finder-map-panel { position: static; }
  .manual-location-fields { grid-template-columns: 1fr 1fr; }
  .manual-location-fields .btn { grid-column: 1 / -1; }
  .finder-filter-panel { padding: 1.1rem; }
}
@media (max-width: 575.98px) {
  .finder-heading h1 { font-size: 2.3rem; }
  .finder-filters, .manual-location-fields { grid-template-columns: 1fr; gap: .5rem; }
  .finder-filter-actions > .btn { margin-left: 0; }
  .finder-filter-actions { gap: .6rem; }
  .finder-filter-actions > .checkbox-label { width: 100%; }
  .facility-card { padding: 1.1rem; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

### `static/js/location.js`

Location success and failure handling is shared; no tracking loop or local storage.

```javascript
"use strict";

(() => {
  const form = document.querySelector("[data-location-form]");
  if (!form) return;
  const button = form.querySelector("[data-location-button]");
  const label = form.querySelector("[data-location-label]");
  const spinner = form.querySelector("[data-location-spinner]");
  const feedback = document.getElementById("location-feedback");
  const latitudeInput = form.elements.namedItem("latitude");
  const longitudeInput = form.elements.namedItem("longitude");
  const manual = form.querySelector("[data-manual-location]");
  if (!button || !latitudeInput || !longitudeInput) return;

  function setLoading(loading) {
    button.disabled = loading;
    button.setAttribute("aria-busy", String(loading));
    spinner.hidden = !loading;
    label.textContent = loading ? "Finding location…" : "Use my location";
  }

  function failure(message) {
    setLoading(false);
    feedback.textContent = message + " Search by name or address, enter coordinates, or try the demo location.";
    if (manual) manual.open = true;
  }

  button.addEventListener("click", () => {
    if (!window.isSecureContext) {
      failure("Location needs HTTPS (or localhost during development).");
      return;
    }
    if (!navigator.geolocation) {
      failure("Your browser cannot share a location.");
      return;
    }
    setLoading(true);
    feedback.textContent = "Finding your location. Your browser may ask for permission.";
    try {
      navigator.geolocation.getCurrentPosition((position) => {
        const { latitude, longitude } = position.coords;
        if (!Number.isFinite(latitude) || !Number.isFinite(longitude) ||
            Math.abs(latitude) > 90 || Math.abs(longitude) > 180) {
          failure("We couldn't read a valid location.");
          return;
        }
        latitudeInput.value = latitude.toFixed(6);
        longitudeInput.value = longitude.toFixed(6);
        // Prevent a bad field in closed <details> from being unfocusable.
        if (manual) manual.open = true;
        setLoading(false);
        feedback.textContent = "Location received. Finding nearby facilities…";
        form.requestSubmit();
      }, (error) => {
        const messages = {
          1: "Location permission was declined. That's okay.",
          2: "Your location is unavailable right now.",
          3: "Finding your location took too long. You can try again.",
        };
        failure(messages[error.code] || "We couldn't get your location.");
      }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 });
    } catch {
      failure("We couldn't get your location.");
    }
  });
  form.addEventListener("invalid", () => {
    if (manual) manual.open = true;
  }, true);
})();
```

### `static/js/facilities.js`

Leaflet uses safe popup nodes, accessible labelled pins and a list fallback.

```javascript
"use strict";

(() => {
  const element = document.getElementById("facility-map");
  const dataElement = document.getElementById("facility-map-data");
  const feedback = document.getElementById("map-feedback");
  if (!element || !dataElement) return;
  if (!window.L) {
    feedback.textContent = "The map couldn't load. You can still use every facility card.";
    return;
  }

  try {
    const data = JSON.parse(dataElement.textContent);
    const map = L.map(element, { scrollWheelZoom: false });
    const points = [];
    const markers = new Map();
    // OSM attribution remains visible; normal browser caching is preserved.
    const tiles = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
    });
    tiles.on("tileerror", () => {
      feedback.textContent = "Some map tiles couldn't load. Pins and the facility list are still available.";
    });
    tiles.addTo(map);

    data.results.forEach((facility, index) => {
      const point = [facility.latitude, facility.longitude];
      points.push(point);
      const marker = L.marker(point, {
        title: facility.name,
        alt: `${index + 1}. ${facility.name}${facility.is_demo ? " — FAKE sample" : ""}`,
        icon: L.divIcon({
          className: `facility-pin${facility.is_demo ? " facility-pin-demo" : ""}`,
          html: `<span>${index + 1}</span>${facility.is_demo ? '<small>Demo</small>' : ""}`,
          iconSize: [48, 48], iconAnchor: [24, 48], popupAnchor: [0, -48],
        }),
      });
      // Leaflet creates the marker DOM only after the map has a view.
      marker.on("add", () => {
        marker.getElement().setAttribute("aria-label", `${index + 1}. ${facility.name}${facility.is_demo ? " — FAKE sample" : ""}`);
      }).addTo(map);
      const popup = document.createElement("div");
      const title = document.createElement("strong");
      title.textContent = facility.name;
      const description = document.createElement("p");
      description.textContent = facility.is_demo ? "FAKE sample. Not a real facility." : facility.type_label;
      const link = document.createElement("a");
      link.href = `#facility-${facility.id}`;
      link.textContent = "View facility card";
      link.className = "map-card-link";
      link.addEventListener("click", () => {
        document.getElementById(`facility-${facility.id}`).focus();
      });
      popup.append(title, description, link);
      marker.bindPopup(popup);
      markers.set(String(facility.id), marker);
    });

    if (data.origin) {
      const origin = [data.origin.latitude, data.origin.longitude];
      points.push(origin);
      const originMarker = L.marker(origin, {
        title: "Search location", alt: "Search location",
        icon: L.divIcon({ className: "search-location-pin", html: "<span>◎</span>", iconSize: [44, 44] }),
      });
      originMarker.on("add", () => {
        originMarker.getElement().setAttribute("aria-label", "Search location");
      }).addTo(map).bindPopup("Search location (the coordinates you supplied)");
    }
    if (points.length) map.fitBounds(points, { padding: [32, 32], maxZoom: 14 });
    else map.setView([22.5, 79], 4);
    feedback.textContent = data.results.length
      ? "Map ready. Select a numbered pin to see its facility."
      : "No facilities match this search. Try widening your filters.";

    document.querySelectorAll("[data-show-on-map]").forEach((button) => {
      const marker = markers.get(button.dataset.showOnMap);
      if (!marker) return;
      button.hidden = false;
      button.addEventListener("click", () => {
        map.setView(marker.getLatLng(), 15);
        marker.openPopup();
        element.scrollIntoView({ block: "center", behavior: "auto" });
        marker.getElement().focus();
      });
    });
  } catch {
    feedback.textContent = "The map is unavailable right now. Please use the facility list.";
  }
})();
```

### `facilities/test_nearby.py`

Search and API regression tests use Django's isolated test database.

```python
from decimal import Decimal
from math import pi

from django.core.paginator import InvalidPage
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .forms import FacilitySearchForm
from .models import Facility, Speciality
from .services import EARTH_RADIUS_KM, FacilityMatch, haversine_km, search_facilities
from .tests import facility_data


class HaversineTests(SimpleTestCase):
    def test_identical_points_are_zero(self):
        self.assertEqual(haversine_km(0, 0, Decimal("0"), Decimal("0")), 0)

    def test_equatorial_degree_and_symmetry(self):
        expected = EARTH_RADIUS_KM * pi / 180
        self.assertAlmostEqual(haversine_km(0, 0, 0, 1), expected, places=8)
        self.assertAlmostEqual(haversine_km(12, 77, -23, -45), haversine_km(-23, -45, 12, 77))

    def test_antipodes_poles_and_date_line(self):
        self.assertAlmostEqual(haversine_km(0, 0, 0, 180), EARTH_RADIUS_KM * pi)
        self.assertAlmostEqual(haversine_km(90, 0, 90, 180), 0)
        self.assertLess(haversine_km(0, 179.9, 0, -179.9), 23)


class FacilitySearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.speciality = Speciality.objects.create(name="Demo care", slug="demo-care")
        cls.other_speciality = Speciality.objects.create(name="Demo care two", slug="demo-care-two")
        cls.near = Facility.objects.create(**facility_data(
            name="Z FAKE Near", latitude=0, longitude=0, is_24x7=True,
            demo_key="near-demo",
        ))
        cls.near.specialities.set([cls.speciality, cls.other_speciality])
        cls.far = Facility.objects.create(**facility_data(
            name="A FAKE Far", latitude=0, longitude=1, facility_type="pharmacy",
        ))
        cls.hidden = Facility.objects.create(**facility_data(
            name="Hidden FAKE", latitude=0, longitude=0, is_active=False,
        ))

    def results(self, **params):
        form = FacilitySearchForm(params)
        self.assertTrue(form.is_valid(), form.errors)
        return search_facilities(form.cleaned_data)

    def test_no_coordinates_sorts_by_name_without_inventing_distance(self):
        page = self.results()
        self.assertEqual([m.facility for m in page], [self.far, self.near])
        self.assertTrue(all(m.distance_km is None for m in page))

    def test_zero_coordinates_are_valid_and_sort_by_distance(self):
        page = self.results(latitude="0", longitude="0")
        self.assertEqual([m.facility for m in page], [self.near, self.far])
        self.assertEqual(page[0].distance_km, 0)
        self.assertAlmostEqual(page[1].distance_km, 111.195, places=3)

    def test_combined_filters_and_inactive_exclusion(self):
        page = self.results(latitude=0, longitude=0, facility_type="hospital",
                            speciality="demo-care", open_24x7="on", radius_km=5)
        self.assertEqual([m.facility for m in page], [self.near])
        self.assertEqual(self.results(facility_type="pharmacy").object_list[0].facility, self.far)

    def test_name_address_and_speciality_search_avoids_m2m_duplicates(self):
        for query in ("Near", "FAKE test address", "Demo care"):
            with self.subTest(query=query):
                page = self.results(q=query)
                ids = [m.facility.pk for m in page]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertIn(self.near.pk, ids)
                self.assertNotIn(self.hidden.pk, ids)
        self.assertEqual(self.results(q="  z   FAKE   Near  ").paginator.count, 1)

    def test_radius_no_matches_and_inclusive_boundary(self):
        self.assertEqual(self.results(latitude=0, longitude=0, radius_km=1).paginator.count, 1)
        self.assertEqual(self.results(latitude=50, longitude=50, radius_km=1).paginator.count, 0)
        distance = haversine_km(0, 0, 0, 1)
        self.assertEqual(self.results(latitude=0, longitude=0, radius_km=distance).paginator.count, 2)

    def test_invalid_parameters_are_rejected(self):
        for params in (
            {"latitude": "0"}, {"longitude": "0"}, {"latitude": "91", "longitude": "0"},
            {"latitude": "0", "longitude": "-181"}, {"latitude": "NaN", "longitude": "0"},
            {"latitude": "0", "longitude": "Infinity"}, {"latitude": "bad", "longitude": "0"},
            {"radius_km": "5"}, {"latitude": "0", "longitude": "0", "radius_km": "0"},
            {"latitude": "0", "longitude": "0", "radius_km": "501"},
            {"facility_type": "invalid"}, {"speciality": "missing"},
            {"q": "x" * 121}, {"page": "0"}, {"page": "bad"},
        ):
            with self.subTest(params=params):
                self.assertFalse(FacilitySearchForm(params).is_valid())

    def test_coordinate_boundaries_are_valid(self):
        for latitude, longitude in ((90, 180), (-90, -180), (0, 0)):
            self.assertTrue(FacilitySearchForm({"latitude": latitude, "longitude": longitude}).is_valid())

    def test_distance_ties_have_deterministic_name_and_pk_order(self):
        same = Facility.objects.create(**facility_data(name=self.near.name, latitude=0, longitude=0))
        page = self.results(latitude=0, longitude=0)
        self.assertEqual([m.facility.pk for m in page][:2], [self.near.pk, same.pk])

    def test_pagination_and_out_of_range(self):
        for index in range(23):
            Facility.objects.create(**facility_data(name=f"FAKE extra {index:02d}"))
        page = self.results(page=2)
        self.assertEqual(page.paginator.count, 25)
        self.assertEqual(len(page.object_list), 5)
        with self.assertRaises(InvalidPage):
            self.results(page=99)

    def test_demo_actions_and_all_zero_phone_are_disabled(self):
        demo = FacilityMatch(self.near, 0)
        self.assertIsNone(demo.call_url)
        self.assertIsNone(demo.directions_url)
        self.assertIsNone(FacilityMatch(self.far, None).call_url)

    def test_ordinary_directions_only_include_destination(self):
        match = FacilityMatch(self.far, None)
        self.assertTrue(match.directions_url.startswith("https://www.google.com/maps/dir/?api=1&destination="))
        self.assertNotIn("origin=", match.directions_url)
        # Intentionally fictional format-only phone, used in an isolated test DB.
        self.far.phone = "+0000000001"
        self.assertEqual(match.call_url, "tel:+0000000001")


class NearbyViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.demo = Facility.objects.create(**facility_data(demo_key="view-demo", latitude=0, longitude=0))
        cls.hidden = Facility.objects.create(**facility_data(name="Hidden FAKE facility", is_active=False))

    def test_public_html_and_api_are_available_without_login(self):
        response = self.client.get(reverse("facilities:nearby"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.demo.name)
        self.assertNotContains(response, self.hidden.name)
        self.assertContains(response, "FAKE sample")
        self.assertContains(response, "This app does not replace calling 112")
        self.assertContains(response, "Call unavailable")
        self.assertContains(response, "Directions unavailable")
        self.assertNotContains(response, 'href="tel:0000000000"')
        api = self.client.get(reverse("facilities:nearby_api"))
        self.assertEqual(api.status_code, 200)
        self.assertEqual(api.json()["count"], 1)

    def test_html_and_api_have_same_filtered_order_and_distances(self):
        Facility.objects.create(**facility_data(name="Far FAKE", latitude=0, longitude=1))
        params = {"latitude": 0, "longitude": 0, "radius_km": 150, "facility_type": "hospital"}
        html = self.client.get(reverse("facilities:nearby"), params)
        api = self.client.get(reverse("facilities:nearby_api"), params).json()
        self.assertEqual([m.facility.pk for m in html.context["page_obj"]], [r["id"] for r in api["results"]])
        self.assertEqual(api["results"][0]["distance_km"], 0)
        self.assertContains(html, "0.00 km away")

    def test_api_redacts_demo_phone_and_actions_and_excludes_internal_fields(self):
        result = self.client.get(reverse("facilities:nearby_api")).json()["results"][0]
        for key in ("phone", "call_url", "directions_url", "distance_km"):
            self.assertIsNone(result[key])
        self.assertIs(result["is_demo"], True)
        self.assertIsInstance(result["latitude"], (int, float))
        for key in ("demo_key", "created_at", "updated_at", "user", "operator_notes"):
            self.assertNotIn(key, result)

    def test_invalid_search_returns_useful_400_on_both_endpoints(self):
        for name in ("nearby", "nearby_api"):
            with self.subTest(name=name):
                response = self.client.get(reverse(f"facilities:{name}"), {"latitude": 0})
                self.assertEqual(response.status_code, 400)
                self.assertIn("Enter both latitude and longitude", response.content.decode())
        response = self.client.get(reverse("facilities:nearby"), {"latitude": "NaN", "longitude": 0})
        self.assertContains(response, "Please check your search", status_code=400)

    def test_non_get_requests_cannot_change_facilities(self):
        for name in ("nearby", "nearby_api"):
            self.assertEqual(self.client.post(reverse(f"facilities:{name}"), {"name": "Changed"}).status_code, 405)
        self.demo.refresh_from_db()
        self.assertEqual(self.demo.name, "FAKE Test Hospital")

    def test_cache_and_cross_origin_referrer_policy(self):
        for name in ("nearby", "nearby_api"):
            response = self.client.get(reverse(f"facilities:{name}"), {"latitude": 0, "longitude": 0})
            self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(self.client.get(reverse("facilities:nearby"))["Referrer-Policy"], "strict-origin-when-cross-origin")

    def test_name_is_escaped_in_cards_and_json_script(self):
        self.demo.name = "</script><img src=x onerror=alert(1)>"
        self.demo.save()
        response = self.client.get(reverse("facilities:nearby"))
        self.assertNotContains(response, self.demo.name)
        self.assertContains(response, r"\u003C/script\u003E")
        self.assertContains(response, "&lt;/script&gt;")

    def test_no_matches_is_a_useful_empty_state(self):
        response = self.client.get(reverse("facilities:nearby"), {"q": "no-match"})
        self.assertContains(response, "No matches this time.")
        self.assertEqual(response.context["map_data"]["results"], [])

    def test_page_links_keep_filters_and_map_only_contains_current_page(self):
        for index in range(22):
            Facility.objects.create(**facility_data(name=f"FAKE page {index:02d}"))
        params = {"q": "FAKE", "facility_type": "hospital", "latitude": 0, "longitude": 0, "page": 1}
        html = self.client.get(reverse("facilities:nearby"), params)
        self.assertEqual(len(html.context["map_data"]["results"]), 20)
        self.assertIn("facility_type=hospital", html.context["next_query"])
        self.assertIn("latitude=0", html.context["next_query"])
        api = self.client.get(reverse("facilities:nearby_api"), params).json()
        self.assertEqual(api["count"], 23)
        self.assertIn("page=2", api["next"])
        self.assertIn("facility_type=hospital", api["next"])
        params["page"] = 2
        last = self.client.get(reverse("facilities:nearby_api"), params).json()
        self.assertEqual(len(last["results"]), 3)
        self.assertIsNone(last["next"])
        self.assertIsNotNone(last["previous"])

    def test_missing_page_returns_404(self):
        for name in ("nearby", "nearby_api"):
            self.assertEqual(self.client.get(reverse(f"facilities:{name}"), {"page": 99}).status_code, 404)

    def test_home_and_navigation_link_to_live_search(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'action="/facilities/"')
        self.assertContains(response, 'href="/facilities/?facility_type=pharmacy"')
        self.assertNotContains(response, "Results and maps are coming soon")
        self.assertContains(response, "SOS sharing and ambulance booking are previews only")
```

### `facilities/frontend_tests.cjs`

Node's built-in modules exercise browser failure paths without requesting real GPS.

```javascript
// Isolated browser-API mocks: no live location, phone call or map request is made.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const scripts = path.join(__dirname, "..", "static", "js");
const locationCode = fs.readFileSync(path.join(scripts, "location.js"), "utf8");
const mapCode = fs.readFileSync(path.join(scripts, "facilities.js"), "utf8");
let checks = 0;
function test(name, run) {
  run();
  checks += 1;
  console.log(`PASS ${name}`);
}
function element() {
  return {
    hidden: true, disabled: false, textContent: "", value: "", open: false,
    attributes: {}, events: {}, children: [],
    setAttribute(name, value) { this.attributes[name] = value; },
    addEventListener(name, callback) { this.events[name] = callback; },
    append(...children) { this.children.push(...children); },
  };
}
function locationFixture({ secure = true, available = true } = {}) {
  const button = element(), label = element(), spinner = element(), feedback = element();
  const latitude = element(), longitude = element(), manual = element();
  const nodes = {
    "[data-location-button]": button, "[data-location-label]": label,
    "[data-location-spinner]": spinner, "[data-manual-location]": manual,
  };
  let submissions = 0, calls = 0, success, failure, options;
  const form = {
    querySelector: (key) => nodes[key],
    elements: { namedItem: (name) => name === "latitude" ? latitude : longitude },
    requestSubmit: () => { submissions += 1; },
    addEventListener() {},
  };
  vm.runInNewContext(locationCode, {
    document: { querySelector: () => form, getElementById: () => feedback },
    window: { isSecureContext: secure },
    navigator: available ? { geolocation: {
      getCurrentPosition(ok, fail, config) { calls += 1; success = ok; failure = fail; options = config; },
    } } : {},
  });
  return { button, label, spinner, feedback, latitude, longitude, manual,
    click: () => button.events.click(),
    succeed: (lat, lon) => success({ coords: { latitude: lat, longitude: lon } }),
    fail: (code) => failure({ code }),
    get calls() { return calls; }, get submissions() { return submissions; },
    get options() { return options; },
  };
}

test("location is requested only on a tap, with a finite timeout and no cached fix", () => {
  const state = locationFixture();
  assert.equal(state.calls, 0);
  state.click();
  assert.equal(state.calls, 1);
  assert.equal(state.button.disabled, true);
  assert.equal(state.spinner.hidden, false);
  assert.equal(state.options.timeout, 10000);
  assert.equal(state.options.maximumAge, 0);
});
test("success submits validated rounded coordinates, including zero", () => {
  const state = locationFixture();
  state.click();
  state.succeed(0, 77.59000012);
  assert.equal(state.latitude.value, "0.000000");
  assert.equal(state.longitude.value, "77.590000");
  assert.equal(state.submissions, 1);
  assert.equal(state.button.disabled, false);
});
test("permission denial keeps the page usable and reveals manual entry", () => {
  const state = locationFixture();
  state.click(); state.fail(1);
  assert.match(state.feedback.textContent, /permission was declined/);
  assert.match(state.feedback.textContent, /Search by name or address/);
  assert.equal(state.manual.open, true);
  assert.equal(state.submissions, 0);
  assert.equal(state.button.disabled, false);
});
test("timeouts and unavailable positions stop the spinner", () => {
  for (const code of [2, 3, 99]) {
    const state = locationFixture();
    state.click(); state.fail(code);
    assert.equal(state.spinner.hidden, true);
    assert.equal(state.submissions, 0);
    assert.match(state.feedback.textContent, /demo location/);
  }
});
test("NaN, infinity and out-of-range locations never submit", () => {
  for (const [lat, lon] of [[NaN, 0], [0, Infinity], [91, 0], [0, -181]]) {
    const state = locationFixture();
    state.click(); state.succeed(lat, lon);
    assert.equal(state.submissions, 0);
    assert.match(state.feedback.textContent, /valid location/);
  }
});
test("insecure and unsupported browsers get a fallback without a request", () => {
  for (const options of [{ secure: false }, { available: false }]) {
    const state = locationFixture(options);
    state.click();
    assert.equal(state.calls, 0);
    assert.match(state.feedback.textContent, /Search by name or address/);
  }
});
test("shared location script safely ignores pages without its form", () => {
  vm.runInNewContext(locationCode, { document: { querySelector: () => null } });
});
test("missing Leaflet leaves a helpful list fallback", () => {
  const feedback = element();
  vm.runInNewContext(mapCode, {
    document: { getElementById: (id) => id === "map-feedback" ? feedback : element() }, window: {},
  });
  assert.match(feedback.textContent, /still use every facility card/);
});
test("map popups treat hostile facility text as text, and tile errors preserve the list", () => {
  const feedback = element(), created = [], tileEvents = {};
  const payload = { origin: null, results: [{ id: 1, name: "<img onerror=alert(1)>",
    type_label: "Hospital", latitude: 0, longitude: 0, is_demo: true }] };
  const data = { textContent: JSON.stringify(payload) };
  let popup, markerElement = element(), mapLoaded = false;
  const addCallbacks = [];
  const map = { fitBounds() { mapLoaded = true; addCallbacks.forEach((callback) => callback()); } };
  const L = {
    map: () => map, divIcon: (config) => config,
    tileLayer: () => ({ on(name, callback) { tileEvents[name] = callback; }, addTo() {} }),
    marker: () => ({ addTo() { return this; },
      on(name, callback) { assert.equal(name, "add"); addCallbacks.push(callback); return this; },
      getElement() { assert.equal(mapLoaded, true); return markerElement; },
      bindPopup(node) { popup = node; return this; } }),
  };
  vm.runInNewContext(mapCode, {
    document: {
      getElementById: (id) => id === "map-feedback" ? feedback : id === "facility-map-data" ? data : element(),
      createElement: () => { const node = element(); created.push(node); return node; },
      querySelectorAll: () => [],
    }, window: { L }, L,
  });
  assert.equal(popup.children[0].textContent, payload.results[0].name);
  assert.equal(popup.children[1].textContent, "FAKE sample. Not a real facility.");
  assert.match(markerElement.attributes["aria-label"], /FAKE sample/);
  assert.match(feedback.textContent, /Map ready/);
  tileEvents.tileerror();
  assert.match(feedback.textContent, /facility list are still available/);
});
console.log(`${checks} frontend checks passed.`);
```

Stop here for this step. Say **"next"** when you are ready for SOS location capture and contact sharing.
