# MEDTAP — Medical Emergency App

A mobile-friendly Django project for finding nearby healthcare facilities,
maintaining a private medical profile and sharing an emergency location.

**This app does not replace calling 112.** SOS sharing is manual. Ambulance
requests are project records; no real dispatch service is connected.

## Features

- Registration, login, private medical profiles and emergency contacts.
- Hospital, clinic, pharmacy and blood-bank management through Django admin.
- Nearby facility search with Haversine distance, filters and a Leaflet map.
- Saved SOS location snapshots with WhatsApp/SMS share links and copy fallback.
- Project ambulance requests, operator permissions and a recorded status timeline.
- Adult first-aid summaries and Indian helpline references with source metadata.
- Responsive Bootstrap UI and small read-only REST APIs.

## Requirements

- Python 3.12 or newer; this project has been tested with Python 3.14.
- Packages pinned in `requirements.txt`: Django, Django REST Framework and python-decouple.
- SQLite for local development. PostgreSQL/PostGIS support is not configured yet.
- Node.js on PATH only if running the JavaScript checks.

Bootstrap, Bootstrap Icons and Leaflet are included locally. Internet access is
needed for OpenStreetMap tiles and Google Fonts; the font has a system fallback.
Browser location access works on localhost or HTTPS and requires permission.

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

### Optional sample content

Run these in another terminal from the project folder:

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo_facilities
.\.venv\Scripts\python.exe manage.py seed_firstaid
```

The facility command creates eight clearly labelled FAKE facilities, seven active,
with synthetic coordinates and dummy phone `0000000000`. Their call/directions
actions are disabled. Choose **Try demo location** on the facility page to browse
them. Neither command creates users or patient records.

The first-aid command supplies five adult educational guides and three official
helpline references. Sources were checked on 12 November 2026; clinical review of
the app's summaries is not recorded. Re-seeding preserves existing edits and does
not claim a fresh source check. See [source notes](FIRST_AID_SOURCES.md).

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

This runs Django system checks, migration drift detection, **192 Django tests**
and **38 JavaScript checks**, stopping on failure. Tests use a separate test
database and temporary child-process settings; your `.env` is unchanged.

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
viewed area to the map provider. Stored SOS coordinates remain until removed.

This repository contains a local-development project. Production hosting,
HTTPS/security settings and a data-retention policy require separate preparation.
Deployment is not configured yet.

See [FIRST_AID_SOURCES.md](FIRST_AID_SOURCES.md) for medical-content provenance and
[THIRD_PARTY.md](THIRD_PARTY.md) for asset licenses and references.
