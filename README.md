# MEDTAP — Medical Emergency App

The project now has its configuration, data models, home page, registration,
login/logout, medical profiles, emergency-contact management, facility admin,
nearby facility search, a read-only facility API, private SOS location sharing,
project ambulance requests with an operator queue, adult first-aid guides and
source-checked Indian helpline references.
Start with [STEP_1.md](STEP_1.md) for the original setup, then read
[UI_REDESIGN.md](UI_REDESIGN.md) for the current Framer-inspired UI and complete
updated code. [UI_STEP_1.md](UI_STEP_1.md) preserves the earlier UI version.
The guides contain file-by-file code, commands and viva explanations. The latest
account feature is documented in [STEP_2.md](STEP_2.md), including all current
shared-style/template changes and the account tests.

Step 4 is complete: [STEP_4.md](STEP_4.md) contains the current search code,
Haversine explanation, API examples, Leaflet setup and verification steps.
[STEP_3.md](STEP_3.md) covers the facility admin and fake sample-data command.
Step 5 is complete: [STEP_5.md](STEP_5.md) explains SOS capture, retry protection,
private saved requests and manual WhatsApp/SMS sharing. It contains complete current
files, commands and viva notes. Step 6 is complete: [STEP_6.md](STEP_6.md) contains
the ambulance workflow, operator permissions, status history, migration and current
shared files. Step 7 is complete: [STEP_7.md](STEP_7.md) covers the first-aid library,
helplines, admin editing, public APIs and source metadata. Medical provenance and
scope are documented in [FIRST_AID_SOURCES.md](FIRST_AID_SOURCES.md).
Step 8 is complete: [STEP_8.md](STEP_8.md) contains the current shared UI files,
mobile overflow fixes, keyboard navigation, password visibility controls,
script-free fallbacks and branded error pages. It includes full copy-paste code,
commands, browser verification and viva notes. Step 9 is complete:
[STEP_9.md](STEP_9.md) adds cross-app workflows with CSRF checks, database-invariant
tests and one command for project verification. It includes complete new source,
a coverage inventory and viva notes. Deployment is Step 10, after "next".

The current design uses Mediso from Framer Marketplace as its main reference:
spacious typography, a photo-led hero, integrated search, clear service cards and
a dark footer. The implementation and illustrative portrait are original.

Run from PowerShell in this directory:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver
```

Run all project checks with the same virtual environment (Node.js must be on PATH):

```powershell
.\.venv\Scripts\python.exe scripts/check_project.py
```

This checks configuration, migration drift, all Django tests and all four
JavaScript check files. It stops on failure. Test settings use a generated
temporary signing key in child processes; your `.env` and running server are
unchanged. Test records use Django's separate test database.

Open **http://127.0.0.1:8000/** for the home page. The built-in Django admin remains
at **http://127.0.0.1:8000/admin/**. Choose the .venv interpreter in VS Code.

- Create an account: **http://127.0.0.1:8000/accounts/register/**
- Login: **http://127.0.0.1:8000/accounts/login/**
- Your private medical profile: **http://127.0.0.1:8000/accounts/profile/**

Registration creates a medical profile and signs you in. Save medical details,
then add/edit/remove emergency contacts and choose a primary contact. Sign out
uses a CSRF-protected POST. Email is optional and login uses your username.
If registration is rejected, the focused error summary says the account was not
created and lists the exact field errors. Correct them before trying to log in.

Run the account tests:

```powershell
.\.venv\Scripts\python.exe manage.py test accounts
```

Facility admin: **http://127.0.0.1:8000/admin/facilities/facility/**. Use a superuser
or a staff account with the relevant permissions; ordinary registration does not
grant admin access. Create an admin account if needed:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

The facility migration has been applied and eight FAKE facilities are seeded.
To add any missing demo records again while preserving existing edits:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo_facilities
.\.venv\Scripts\python.exe manage.py test facilities accounts
```

Find facilities at **http://127.0.0.1:8000/facilities/**. Use **Try demo location**
to see seven active FAKE samples sorted by approximate distance. Filter by type,
speciality, 24×7 flag and an optional distance radius. Name/address search works
without JavaScript or location permission. Coordinates can also be entered manually.
The map and list show the same page of up to 20 results. FAKE records have no call
or directions actions. Ordinary entries are not independently verified by MEDTAP.

Read-only JSON API (no login required):
**http://127.0.0.1:8000/facilities/api/nearby/?latitude=12.97&longitude=77.59&radius_km=5**.
It uses the same validation, filters and distance calculation as the HTML page.

```powershell
.\.venv\Scripts\python.exe manage.py test facilities accounts
node facilities/frontend_tests.cjs
node emergency/frontend_tests.cjs
node emergency/ambulance_frontend_tests.cjs
node core/ui_frontend_tests.cjs
```

There are 192 Django tests and 38 isolated frontend checks (9 search, 12 SOS,
8 ambulance, 9 shared UI). Run the full suite to include the shared UI tests:

```powershell
.\.venv\Scripts\python.exe manage.py test
```

Node is needed only for frontend checks, not to run Django. No new model migration
is needed in Steps 4, 5, 8 or 9. Step 6 adds a version field and status-event model:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py setup_ambulance_operators
```

The migration is applied and the operator group is created. No existing user has
been assigned to it or promoted. A superuser can use the dashboard immediately.
For a separate operator, use the admin Users page to assign **Ambulance operators**
and enable **Staff status**. Both view/change ambulance permissions and staff
status are required; ordinary accounts cannot use the queue.

- Your transport requests: **http://127.0.0.1:8000/emergency/ambulance/**
- Operator queue: **http://127.0.0.1:8000/emergency/operators/ambulances/**

Choose a saved active SOS location, review it, and submit one project request.
Operators move it Requested → Accepted → On the way → Completed. Status events
record the actor and time; stale forms return a conflict instead of overwriting
newer edits. The owner page checks status every 10 seconds while visible, stops
on completion/errors, and also has a manual refresh link. Internal operator notes
are never included in the owner's status response. Existing pre-Step-6 records
have no invented event history. SOS and ambulance lifecycles remain separate.

This is a project queue, not a connected dispatch service. No real provider is
contacted. A facility reference does not verify an ambulance or provider capacity;
FAKE references stay labelled as samples. Call 112 in a real emergency.

First-aid library: **http://127.0.0.1:8000/first-aid/**. It has five adult educational
summaries: CPR, severe external bleeding, burns/scalds, choking and recovery position.
Sources were checked on **12 November 2026**. Clinical review of our summaries is
not recorded, and the pages say so. Original references are linked from every guide.

Helplines: **http://127.0.0.1:8000/first-aid/helplines/**. The cards distinguish
nationwide 112 from state/UT-dependent 108 and 102, with 102 described as patient
transport. No live test calls were made. To recreate missing seeded content:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_firstaid
```

The Step 7 migration and seed are already applied. Re-seeding preserves edits and
does not automatically update dates or republish records. Public views/APIs hide
unpublished, undated, future-dated, empty or unsourced guides, and inactive or
unverified helplines. Manage content through the Firstaid section of Django admin.

Public read-only APIs:

- `/first-aid/api/guides/` — search/paginated catalogue
- `/first-aid/api/guides/adult-cpr/` — ordered steps and source/review metadata
- `/first-aid/api/helplines/` — number, coverage, check date and call link

The home page includes the disclaimer **"This app does not replace calling 112."**
SOS is available at **http://127.0.0.1:8000/emergency/sos/** after signing in.
On any page, a signed-in user's SOS button requests a fresh browser location,
saves an EmergencyRequest using a CSRF-protected POST, and opens a private sharing
screen. You choose a recipient and press Send in WhatsApp/SMS yourself; the app
does not send messages, confirm delivery or book an ambulance. Manual coordinate
entry and message copying provide fallbacks. Requests are location snapshots,
not live tracking. A retry from the same button uses the same request ID.
Other users cannot view a request even if they know its URL. No medical details
are inserted into the share message. The stored location remains in SQLite until
removed; a production retention policy is part of later deployment work.

Directory search still sends coordinates in GET URLs, which may appear in history
and server logs. Search does not save them to a profile or emergency record. SOS
explicitly stores them with the signed-in account through POST. Map tile requests
reveal the viewed area to OpenStreetMap. Internet access is required for map tiles.

The eight sample facilities have FAKE names/addresses, synthetic coordinates, a
read-only demo identifier and the dummy phone 0000000000. They are learning data.
The facility command seeds no patient data, first-aid instructions or helpline
records; `seed_firstaid` supplies the separately documented educational content.
The visible
112 call shortcut is an ordinary telephone link, independent of the app's database.

See [THIRD_PARTY.md](THIRD_PARTY.md) for asset versions, licenses and references.
