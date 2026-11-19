# MEDTAP — Medical Emergency App

A mobile-friendly Django project for finding nearby healthcare facilities,
maintaining a private medical profile and sharing an emergency location.

**This app does not replace calling 112.** SOS sharing is manual. Ambulance
requests are project records; no real dispatch service is connected.

## Features

- Registration, login, private medical profiles and emergency contacts.
- Hospital, clinic, pharmacy and blood-bank management through Django admin.
- Real OpenStreetMap facility discovery with Haversine distance, filters and a Leaflet map.
- Saved SOS location snapshots with WhatsApp/SMS share links and copy fallback.
- Project ambulance requests, operator permissions and a recorded status timeline.
- Adult first-aid summaries and Indian helpline references with source metadata.
- Responsive Bootstrap UI and small read-only REST APIs.

## Requirements

- Python 3.12 or newer; this project has been tested with Python 3.14.
- Packages pinned in `requirements.txt`: Django, Django REST Framework and python-decouple.
- SQLite for local storage. No separate database server is required.
- Node.js on PATH only if running the JavaScript checks.

Bootstrap, Bootstrap Icons and Leaflet are included locally. Internet access is
needed for OpenStreetMap tiles and Google Fonts; the font has a system fallback.
Browser location access works on localhost or HTTPS and requires permission.

## Real facility search

Choose **Use my location** on the home or facility page to request a fresh browser
position. The app searches OpenStreetMap for hospitals, clinics, pharmacies and
blood banks around that location, merges ordinary admin-entered facilities and
sorts by approximate straight-line distance. No location is hardcoded or generated.
You can also pan/zoom the map and choose **Search this map area**, or enter coordinates.
Name/address text filters listings in the chosen area; it does not geocode cities.

Cards show the original listing source, available phone/directions links and
mapped opening hours. Missing details stay unknown; 24×7 means the source explicitly
lists `24/7`, not that the facility has been contacted or is confirmed open now.
OSM coverage and tagging vary, including for blood banks and specialities.
Fake sample facilities are excluded from normal public search, HTML and API.

Live search is enabled by default and needs no API key. Optional `.env` settings:

```dotenv
FACILITIES_LIVE_ENABLED=True
FACILITIES_OVERPASS_URL=https://maps.mail.ru/osm/tools/overpass/api/interpreter
FACILITIES_OVERPASS_METHOD=POST
FACILITIES_OVERPASS_FALLBACK_URLS=https://overpass-api.de/api/interpreter
```

The default radius is 5 km, adjustable from 0.1–25 km. A rounded area centre
(approximately 1 km precision) goes to the directory provider, without account,
contact or medical details. Area responses are cached for 15 minutes in ignored
`.cache/`; an outage can use explicitly labelled snapshots up to 24 hours old.
Retrieval time is shown. With no cached or locally managed results, a provider
failure returns HTTP 503 instead of falsely reporting a successful empty search.
At most 2,000 upstream elements are processed; a limit notice advises refining
the radius. The API includes `search` metadata and per-listing `source`,
`source_url` and `opening_hours`. OSM IDs are strings such as `osm-node-123`;
local directory IDs remain integers. OSM records are not silently copied into SQLite.

Searches use VK Maps Overpass by default, with the main Overpass public server
as a backup if it is busy or unreachable. Both return OpenStreetMap data; the configured
hosts are linked in the search page's location privacy information. Each failed
endpoint cools down for 60 seconds while healthy alternatives remain available.
There are at most three distinct endpoint attempts per search. Set
`FACILITIES_OVERPASS_FALLBACK_URLS=` to disable fallback, or provide a comma-separated
list of endpoints you operate or trust. A custom primary URL has no public fallback
by default; if you copied `.env.example`, clear its explicit fallback when switching
to a private provider. Public endpoint information is maintained in the
[OpenStreetMap Overpass instance directory](https://wiki.openstreetmap.org/wiki/Overpass_API#Public_Overpass_API_instances).

After changing `.env`, stop and restart Django; editing `.env` alone does not
reload settings. For an existing installation, also change
`FACILITIES_OVERPASS_METHOD=GET` to `POST` to use the default provider's POST interface.
If all endpoints fail, the server log reports the failed host, error type and HTTP
status without recording query coordinates or provider credentials. A 502/503
usually means the public server is busy; a timeout means it did not respond in time.

The shared public Overpass endpoints are for light, manually triggered use. For a
public launch or dependable capacity, configure a managed or self-hosted provider
and review its service/privacy terms. See the [Overpass usage guidance](https://dev.overpass-api.de/overpass-doc/en/preface/commons.html).
The endpoints are configurable without changing code; providers requiring GET can
use `FACILITIES_OVERPASS_METHOD=GET`. Public services may throttle or time out;
the UI reports this and keeps Call 112 available. No automatic bulk harvesting,
polling or geocoding service is configured.

### Adding an API-key provider later

**OpenStreetMap remains active.** No paid account, API key or Google integration
is needed now. There are two possible future routes:

**1. Keep OpenStreetMap + Leaflet with a managed Overpass provider.**

- Choose a provider that accepts Overpass queries and returns the standard OSM
  `elements` JSON. Confirm its coverage, limits, billing and attribution terms.
- Obtain the complete HTTPS interpreter URL and the authentication instructions
  from that provider. If its key is embedded in the URL path, keep that full URL
  private in `.env` as `FACILITIES_OVERPASS_URL`. Set
  `FACILITIES_OVERPASS_METHOD=GET` or `POST` as instructed by the provider.
- The existing adapter supports a key in the URL path. It currently rejects
  query-string credentials and does not send provider-specific authentication
  headers. A provider requiring either needs a small adapter change first.
- Restart Django and test one nearby search. Endpoint-specific cache keys keep
  the previous provider's cached data separate. Check source links, all four
  categories, missing details and error handling before opening access to users.

Do not substitute a Google Places URL into `FACILITIES_OVERPASS_URL`: the request
and response formats differ. Keeping the same OpenStreetMap data format is what
allows the existing Leaflet interface to continue working.

**2. Switch to Google Places API (New).**

1. Create/select a project in [Google Cloud Console](https://console.cloud.google.com/),
   link billing and enable **Places API (New)**. Review current usage pricing,
   set appropriate API quotas and configure [budget alerts](https://cloud.google.com/billing/docs/how-to/budgets).
   Alerts alone do not impose a hard spending cap. Follow [Google's setup guide](https://developers.google.com/maps/documentation/places/web-service/get-api-key).
2. Create a dedicated server API key. Restrict it to the required API and, when
   your deployment has fixed outbound IP addresses, restrict it to those server
   IPs. A browser key for a future Google Map should be separate and restricted
   to your website origins. Follow [Google's key security guidance](https://developers.google.com/maps/api-security-best-practices).
3. Save the server key only in your local ignored `.env` or your host's secret
   settings. The intended future variable is:

   ```dotenv
   GOOGLE_PLACES_API_KEY=your_private_key_here
   ```

   **This variable is not read by the current application. Adding it alone does
   not activate Google Places.** Never paste a real key into README, templates,
   client-side scripts, screenshots or Git. The browser map key has a different
   role and must not reuse the server key.
4. Add a separate backend provider adapter, loading that variable with decouple.
   Google [Nearby Search (New)](https://developers.google.com/maps/documentation/places/web-service/nearby-search)
   uses POST JSON to `https://places.googleapis.com/v1/places:searchNearby`, with
   `X-Goog-Api-Key` and a deliberately small `X-Goog-FieldMask`. It cannot reuse
   our Overpass query. Map Google types/fields into our facility response and
   validate category coverage against the [current type list](https://developers.google.com/maps/documentation/places/web-service/place-types).
   Do not assume every MEDTAP category, speciality or phone field is returned.
5. Update the UI, attribution, privacy information and caching for that provider.
   Under [Google's Places policies](https://developers.google.com/maps/documentation/places/web-service/policies),
   Places results shown on a map must use a Google Map; results without a map
   still need the required attribution. Do not plot Google Places results on
   our current OSM/Leaflet map or copy them into our OSM snapshot cache. Use only
   storage/caching explicitly allowed by the applicable terms.
6. Add mocked adapter tests for success, missing fields, denied keys, quota
   errors and outages; then make a deliberate small live test and run
   `scripts/check_project.py`. Enable the provider only after those changes are
   implemented and reviewed. An API key does not verify stock, beds or dispatch.

No Google adapter, account, key or paid request has been created by this project.
When you decide to switch, specify the provider; its integration can then be
implemented without sharing your actual key in chat.

## Local setup

Clone the repository, or extract its ZIP and open the project folder:

```powershell
git clone https://github.com/7085ashishraj/MedTep.git MEDTAP
cd MEDTAP
```

In PowerShell, create the environment, install dependencies and create your local
configuration. Run the copy command only when setting up a new `.env`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Paste the generated value after `DJANGO_SECRET_KEY=` in `.env`. Keep it private.
The example also defines `DJANGO_DEBUG=True` and local `DJANGO_ALLOWED_HOSTS`
for development. `.env`, databases, virtual environments and caches are ignored
by Git. Never commit actual credentials or patient data.

On macOS/Linux, use `python3 -m venv .venv`, `.venv/bin/python` instead of
`.\.venv\Scripts\python.exe`, and `cp .env.example .env` instead of `Copy-Item`.
Select the virtual-environment interpreter in VS Code.

Create the database and an admin account, then start the development server:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Open [MEDTAP](http://127.0.0.1:8000/) or [Django admin](http://127.0.0.1:8000/admin/).
Ordinary registration does not grant admin or operator access.

### Educational content

Run these in another terminal from the project folder:

```powershell
.\.venv\Scripts\python.exe manage.py seed_firstaid
```

The first-aid command supplies five adult educational guides and three official
helpline references. Sources were checked on 12 November 2026; clinical review of
the app's summaries is not recorded. Re-seeding preserves existing edits and does
not claim a fresh source check. See [source notes](FIRST_AID_SOURCES.md).
No facility seed is needed for live search. The fake-facility seed command remains
available for development tests, and its records are hidden from public search.

### Operator access

```powershell
.\.venv\Scripts\python.exe manage.py setup_ambulance_operators
```

This creates the **Ambulance operators** group without assigning or promoting
users. A superuser can use the operator dashboard immediately. For another
operator, assign that group and enable **Staff status** through admin. Both view
and change ambulance permissions are required.

Operators advance requests through Requested → Accepted → On the way → Completed.
Status changes record an actor/time; stale edits are rejected. Internal operator
notes are excluded from the owner's status response. No provider is contacted.

## Main pages and APIs

| Page | Path |
| --- | --- |
| Create account / login | `/accounts/register/` · `/accounts/login/` |
| Private medical profile | `/accounts/profile/` |
| Facility search | `/facilities/` |
| Private SOS page | `/emergency/sos/` |
| Your transport requests | `/emergency/ambulance/` |
| Operator queue | `/emergency/operators/ambulances/` |
| First-aid library / helplines | `/first-aid/` · `/first-aid/helplines/` |

Public read-only JSON endpoints:

```text
/facilities/api/nearby/?latitude=12.97&longitude=77.59&radius_km=5
/first-aid/api/guides/
/first-aid/api/guides/adult-cpr/
/first-aid/api/helplines/
```

## Verification

Run all project checks with the project's Python interpreter and Node.js on PATH:

```powershell
.\.venv\Scripts\python.exe scripts/check_project.py
```

This runs Django system checks, migration drift detection, **219 Django tests**
and **41 JavaScript checks**, stopping on failure. Tests use a separate test
database and temporary child-process settings; your `.env` is unchanged.
Provider calls are mocked in automated tests. Separately, the real website/API
was checked against a public Bengaluru city-centre search on 18 November 2026:
787 listings within 5 km, with HTTP 200 from both the HTML page and JSON API
after recovery from an overloaded endpoint. Those are source listings at that time, not a guarantee of completeness
or current availability. No personal GPS position, test calls or messages were used.

To run the Django suite alone:

```powershell
.\.venv\Scripts\python.exe manage.py test
```

## Project structure

```text
accounts/       Authentication, medical profiles and contacts
common/         Shared model and validation utilities
config/         Django settings and root routes
core/           Home page, shared UI and cross-app tests
emergency/      SOS records and project ambulance workflow
facilities/     Directory, search, admin and API
firstaid/       Educational guides, helplines, admin and API
scripts/        Project verification command
static/         Styles, scripts, images and vendored assets/licenses
templates/      Shared layout and application pages
```

## Scope and privacy

Facility distances are approximate; listings do not confirm beds, stock or
emergency capacity. Helplines 108/102 have state/UT-dependent coverage, documented
on the helpline page. First-aid summaries do not replace professional training.

SOS requires sign-in and saves a location snapshot, not live tracking. Users
choose recipients and send messages themselves in WhatsApp/SMS. Medical-profile
details are not inserted into share messages. Search coordinates appear in GET
URLs and may enter browser history/server logs; map tile requests reveal the
viewed area to the map provider. Coarse area-query results are cached separately
from private SOS records. Stored SOS coordinates remain until removed.

This project runs locally with Django and SQLite using the setup instructions above.
Hosting configuration is not included.

See [FIRST_AID_SOURCES.md](FIRST_AID_SOURCES.md) for medical-content provenance and
[THIRD_PARTY.md](THIRD_PARTY.md) for asset licenses and references.
