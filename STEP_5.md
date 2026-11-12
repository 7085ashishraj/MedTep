# Step 5 — SOS location capture and manual sharing

This feature is implemented in your workspace. Steps 1–4 are prerequisites. This
guide contains complete current files and replaces earlier SOS preview markup.
No new Python dependency, secret, database field or migration is required.

## What this step does

For a signed-in user, one SOS tap requests a fresh browser location, submits it
through a CSRF-protected POST and saves an EmergencyRequest. The private result
screen offers a copyable message, Google Maps link, general WhatsApp/SMS composers
and links for eligible saved emergency contacts. You must press Send in the chosen
app. Saving a request does not notify anyone, confirm delivery or dispatch an
ambulance. The timeline describes local saving and manual sharing steps only.

Guests first sign in and return to the SOS page. A GET never creates a record or
starts location capture. If location permission is denied, manual coordinate entry
remains available. Without JavaScript, the same manual POST and sharing links work.

## Current files for this step

```text
MEDTAP/
├── emergency/
│   ├── forms.py                 # UUID and validated Decimal coordinates
│   ├── services.py              # idempotent save, message and composer builders
│   ├── views.py                 # authenticated start/create/detail views
│   ├── urls.py                  # namespaced routes
│   ├── tests.py                 # 25 new Django tests
│   └── frontend_tests.cjs       # 11 isolated SOS browser-API checks
├── templates/
│   ├── base.html                # shared SOS script and CSRF form
│   ├── core/home.html           # live SOS wording
│   ├── emergency/
│   │   ├── start.html           # capture, manual entry, recent owned requests
│   │   └── detail.html          # saved location and manual sharing
│   └── partials/
│       ├── sos_button.html      # reusable desktop/mobile link
│       ├── sos_controls.html    # signed-in CSRF form and progress feedback
│       └── footer.html          # current disclaimer
├── static/
│   ├── css/theme.css            # complete existing theme plus SOS styles
│   └── js/sos.js                # capture, retry, loading and copy fallbacks
└── facilities/test_nearby.py     # existing home wording assertion updated
```

The existing EmergencyRequest model already has UUID ID, user, latitude, longitude,
status and timestamps. This step uses those fields. `active` describes the saved
record's lifecycle; it does not mean a responder has accepted the request.
AmbulanceRequest records are not created in this step.

## Exact commands

Run in the MEDTAP directory in PowerShell:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test emergency accounts facilities
node emergency/frontend_tests.cjs
node facilities/frontend_tests.cjs
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Expect no new migrations to apply, **110 Django tests passing**, **11 SOS frontend
checks passing** and **9 facility frontend checks passing**. Node is needed only
for these isolated frontend checks, not to run the application. Use the existing
development server if it is already running; do not start a second on the same port.
If needed, Ctrl+C stops it so you can restart. Existing `.env` settings are enough.

Use an ordinary account. This step does not require a superuser. If you also need
an admin account for facility management, the unchanged command is:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

## Try it and know what to expect

1. Sign in at [Login](http://127.0.0.1:8000/accounts/login/). Review your emergency
   contacts in your profile. Do not enter a real password into any code or guide.
2. Open [SOS](http://127.0.0.1:8000/emergency/sos/). It explains that saving does not
   contact anyone. The page also lists up to five of your recently saved requests.
3. Tap SOS when you intend to save your location. The browser asks permission if
   necessary. You should see a loading notice while locating and saving, followed
   by **Your request is saved. Now share it.**
4. If permission is denied or unavailable, open **Location unavailable? Enter
   coordinates**. Enter both coordinates and choose **Save entered location**.
   Only enter a location you know to be correct. For a clearly fictional learning
   test, you may use the demo centre `12.970000, 77.590000`; this intentionally
   creates a test request in your local database and does not dispatch anything.
5. Review the timestamp and location before sharing. **Copy message** copies only;
   **Choose in WhatsApp/SMS** opens a composer. Select a recipient and press Send
   yourself. No message is sent by Django. You can also select/copy the text manually.
6. Contacts with local-format numbers can use SMS; direct WhatsApp links require
   a number beginning with `+` and a country code. The app does not guess a country
   code. All-zero placeholders have no direct sharing links. The general WhatsApp
   chooser remains available when no contacts are saved.
7. If saving is uncertain after a connection failure, open **Recently saved** on
   the SOS page. Retrying the same in-page SOS button reuses its request ID. A new
   page load or another tab is a new action, so check recent requests first.

Browser location needs HTTPS or localhost and device permission. The 10-second
location timeout and 15-second network timeout keep the interface from waiting
indefinitely. Automatic capture records one fix; it does not keep tracking you.
SMS body/composer handling depends on the installed app. SMS may be split into
multiple billable messages, so the copyable message is always available.

## What each route does

| Route | Method | Behaviour |
| --- | --- | --- |
| `/emergency/sos/` | GET | Private start form and five recent owned requests; no write |
| `/emergency/sos/create/` | POST | Validate coordinates/UUID and save or return an owned retry |
| `/emergency/sos/<uuid>/` | GET | Private message, recorded location and own contact composers |

The create view returns a redirect for a normal form submission. The shared script
sends `Accept: application/json` and gets `{ "url": "/emergency/sos/<uuid>/",
"created": true }` with HTTP 201, or HTTP 200 and `created: false` for a retry.
This is the same session-authenticated Django view, not a public write API.
Bad input produces 400 and field errors. An expired JSON session produces 401.
Expired HTML sessions return to the GET start page after login, avoiding a 405
from redirecting to a POST-only endpoint. Another user's record is 404 on read;
trying to reuse their UUID is 403. Create still requires CSRF even for JSON responses.

## Viva notes: why the design works

**Validation and ownership.** The form accepts only request ID and coordinates,
with six decimal places and latitude/longitude bounds. NaN, Infinity and incomplete
coordinates are rejected. The server gets `user` from the session and uses the
model's default status, ignoring forged user/status fields. Detail queries include
`user=request.user`; a UUID is never used as a substitute for authentication.
Only your own profile's contacts are loaded. All private responses use no-store.

**Retry protection (idempotency).** The browser generates one UUID for an SOS
action. `get_or_create` uses the unique primary key, so retrying the same action
returns the same row. It checks ownership before returning it. A retry never
changes an existing location, timestamp or status. This protects retries across
different request payloads too. A shared in-flight flag also ignores repeated taps
on the desktop and mobile SOS controls while the same action is pending. The
manual form gets its own server-generated UUID in a hidden field. This is not a
claim of global duplicate detection across tabs, reloads or different action IDs.

**POST/redirect/GET.** Saving changes state and uses CSRF-protected POST. A normal
submission redirects to a GET result, so refreshing the result does not save again.
The automatic path posts FormData with the rendered CSRF token, then navigates to
the server's private result. Captured coordinates never appear in that local URL.

**A snapshot, not a live status.** The result has three honest steps: location
recorded, choose a contact/app, and press Send there. There are no assigned/on-the-way
or delivered indicators because no dispatch or delivery integration exists yet.
No location accuracy or ETA claim is made. Manual coordinates are not verified
GPS. The saved timestamp is the record's creation time, not proof of a live GPS fix.

**A clean messaging boundary.** `build_emergency_message` creates plain text.
`build_share_options(message, phone)` creates encoded links and performs no I/O.
To add Twilio later, implement a separate authenticated POST delivery operation
that accepts the prepared message/recipient, with delivery idempotency. Do not put
a sender into this pure function or the GET detail page: opening a page must never
silently send a message. The current code needs no Twilio credentials or package.

**Privacy.** SOS deliberately stores the account/location/timestamp in SQLite
until removed; it does not expire or delete records automatically. A production
retention policy and database protection belong in deployment work. Only the owner
can read its page, and deleting the user leaves a detached row (`SET_NULL`) that
other users still cannot read. The share text includes no blood group, allergies,
conditions, contact list, account identifier or private detail-page URL. A chosen
recipient can open the Google Maps location without signing into MEDTAP. Opening
a share link passes the message to that service; sending is the user's action.
External links use `noreferrer` to avoid leaking the private request URL.

## Link references

The [official WhatsApp click-to-chat guide](https://faq.whatsapp.com/5913398998672934)
describes international-number paths and a URL-encoded `text` query, including
a general recipient chooser. We use those formats and never assume a local number's
country. The [Google Maps URL guide](https://developers.google.com/maps/documentation/urls/get-started)
documents universal search URLs with `api=1`; these links need no API key.
[RFC 5724](https://www.rfc-editor.org/rfc/rfc5724) specifies SMS URIs including a
message body. Installed-app compatibility still needs device testing.

## Verification completed

- 110 Django tests pass: the previous 85 plus 25 SOS tests covering validation,
  ownership, idempotent retries, CSRF, expired sessions, escaped contact names,
  no medical-data insertion, link encoding and absence of ambulance creation.
- 11 isolated SOS JavaScript checks pass for tap-only capture, duplicate taps,
  CSRF/rounding, denial/timeouts, invalid GPS, uncertain network retry, expired
  login, constrained redirects and clipboard fallback. The 9 search checks pass too.
- System checks and migration-drift checks pass; no new migration.
- Browser review uses a separate ignored fictional preview database. Manual
  creation, saved message, contact placeholder handling and desktop/mobile layouts
  were verified. Phone content does not overflow horizontally. Your real database
  was not used for the visual test. No real GPS permission, message, SMS, WhatsApp
  send or emergency call was exercised. The separate preview server was stopped.

## Complete code, file by file

Create the folders where needed and replace each file below in full. Existing
models, project URLs, accounts code and dependencies remain prerequisites.

### `emergency/forms.py`

One validated form supports both manual POST and automatic capture.

```python
import uuid

from django import forms


class EmergencyRequestForm(forms.Form):
    request_id = forms.UUIDField(widget=forms.HiddenInput, initial=uuid.uuid4)
    latitude = forms.DecimalField(max_digits=8, decimal_places=6, min_value=-90, max_value=90)
    longitude = forms.DecimalField(max_digits=9, decimal_places=6, min_value=-180, max_value=180)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("latitude", "longitude"):
            self.fields[name].widget.attrs.update({
                "class": "form-control", "step": "any", "inputmode": "decimal",
            })
```

### `emergency/services.py`

Saving, plain-text messages and pure composer-link builders are separate functions.

```python
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
```

### `emergency/views.py`

Authenticated function-based views keep creation and viewing separate.

```python
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_GET, require_POST

from accounts.models import EmergencyContact

from .forms import EmergencyRequestForm
from .models import EmergencyRequest
from .services import build_emergency_message, build_share_options, google_maps_url, save_sos_request


@never_cache
@login_required
@require_GET
def start(request):
    return render(request, "emergency/start.html", {
        "form": EmergencyRequestForm(),
        "recent_requests": EmergencyRequest.objects.filter(user=request.user)[:5],
    })


@sensitive_post_parameters()
@never_cache
@require_POST
def create(request):
    wants_json = request.headers.get("Accept") == "application/json"
    if not request.user.is_authenticated:
        if wants_json:
            return JsonResponse({"error": "Sign in again before saving an SOS request."}, status=401)
        # After login, return to a GET page rather than the POST-only create URL.
        return redirect_to_login(reverse("emergency:start"), login_url=reverse("accounts:login"))
    form = EmergencyRequestForm(request.POST)
    if not form.is_valid():
        if wants_json:
            return JsonResponse({"errors": dict(form.errors)}, status=400)
        return render(request, "emergency/start.html", {"form": form}, status=400)
    emergency, created = save_sos_request(user=request.user, **form.cleaned_data)
    url = reverse("emergency:detail", kwargs={"pk": emergency.pk})
    if wants_json:
        return JsonResponse({"url": url, "created": created}, status=201 if created else 200)
    return redirect(url)


@never_cache
@login_required
@require_GET
def detail(request, pk):
    emergency = get_object_or_404(EmergencyRequest, pk=pk, user=request.user)
    message = build_emergency_message(emergency)
    contacts = EmergencyContact.objects.filter(profile__user=request.user).order_by("-is_primary", "name", "pk")
    return render(request, "emergency/detail.html", {
        "emergency": emergency, "share_message": message,
        "maps_url": google_maps_url(emergency),
        "general_share": build_share_options(message),
        "contact_shares": [{"contact": contact, "options": build_share_options(message, contact.phone)} for contact in contacts],
    })
```

### `emergency/urls.py`

App-level namespaced routes are already included by the project's emergency prefix.

```python
from django.urls import path

from . import views

app_name = "emergency"
urlpatterns = [
    path("sos/", views.start, name="start"),
    path("sos/create/", views.create, name="create"),
    path("sos/<uuid:pk>/", views.detail, name="detail"),
]
```

### `templates/partials/sos_button.html`

A normal link works for guests or without JavaScript; signed-in capture enhances it.

```html
<a class="btn sos-button{% if compact %} sos-button-compact{% endif %}" href="{% url 'emergency:start' %}" data-sos-trigger aria-label="SOS: save your location, then choose how to share"{% if describedby %} aria-describedby="{{ describedby }}"{% endif %}>
  <strong>SOS</strong><span>Share</span>
</a>
```

### `templates/partials/sos_controls.html`

The signed-in CSRF form and shared live progress/fallback notice.

```html
{% if user.is_authenticated %}
<form id="sos-request-form" method="post" action="{% url 'emergency:create' %}" hidden>{% csrf_token %}</form>
<div class="sos-feedback" id="sos-feedback" role="status" aria-live="polite" tabindex="-1" hidden>
  <span class="spinner-border spinner-border-sm" id="sos-spinner" aria-hidden="true" hidden></span>
  <p id="sos-feedback-text"></p>
  <a href="{% url 'emergency:start' %}" id="sos-fallback" hidden>Open SOS page for manual entry or saved requests</a>
</div>
{% endif %}
```

### `templates/base.html`

All pages receive the same SOS enhancement, alongside the existing theme and partials.

```html
{% load static %}
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="description" content="MEDTAP is a medical emergency project that helps you find your way to care. In a real emergency, call 112.">
  <meta name="theme-color" content="#023E8A">
  <title>{% block title %}MEDTAP | A little closer to care{% endblock %}</title>
  <link rel="icon" href="{% static 'img/favicon.svg' %}" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'vendor/bootstrap/bootstrap.min.css' %}">
  <link rel="stylesheet" href="{% static 'css/theme.css' %}">
  {% block extra_css %}{% endblock %}
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  {% include 'partials/navbar.html' %}
  <main id="main-content" class="site-main" tabindex="-1">
    {% include 'partials/messages.html' %}
    {% block content %}{% endblock %}
  </main>
  {% include 'partials/footer.html' %}
  {% include 'partials/feature_preview.html' %}
  {% include 'partials/sos_controls.html' %}
  <div class="mobile-emergency-bar" aria-label="Emergency call shortcut">
    <p><strong>Need urgent help?</strong>Call emergency services.</p>
    <div class="mobile-bar-actions">
      {% include 'partials/sos_button.html' with compact=True only %}
      <a href="tel:112" class="btn btn-primary">
        {% include 'partials/icon.html' with name='telephone' class_name='icon-sm' only %} Call 112
      </a>
    </div>
  </div>
  <script src="{% static 'vendor/bootstrap/bootstrap.bundle.min.js' %}" defer></script>
  <script src="{% static 'js/site.js' %}" defer></script>
  <script src="{% static 'js/sos.js' %}" defer></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

### `templates/emergency/start.html`

Calm capture/manual-entry page and recent owned request links.

```html
{% extends 'base.html' %}
{% block title %}SOS location sharing | MEDTAP{% endblock %}
{% block content %}
<section class="account-section"><div class="container sos-page">
  <div class="sos-heading"><p class="eyebrow">A clearer next step</p><h1>Let your people<br>know where you are.</h1><p>Save your location, then send a message to someone you trust.</p></div>
  <div class="sos-critical-note"><strong>In a real emergency, call 112.</strong> Saving here does not notify your contacts, emergency services or an ambulance provider. You must send the message yourself.</div>
  <div class="sos-layout">
    <section class="account-panel sos-start-panel" aria-labelledby="capture-heading">
      <h2 id="capture-heading">Start with your location</h2><p>Tap SOS to request a fresh browser location and save a private request. Keep this page open while it saves.</p>
      {% include 'partials/sos_button.html' with describedby='sos-privacy' only %}
      <p id="sos-privacy" class="field-help">Location is stored with your account. This is a single snapshot, not live tracking. Sharing a message sends that snapshot to the app and recipient you choose.</p>
      <noscript><p>Automatic capture needs JavaScript. Use the manual form below.</p></noscript>
      <hr>
      {% include 'partials/form_errors.html' with form=form error_heading='Your request was not saved' only %}
      <details{% if form.errors %} open{% endif %}><summary class="sos-manual-summary">Location unavailable? Enter coordinates</summary>
        <p class="field-help">Only enter coordinates you know are correct. Manual entry does not verify your live location.</p>
        <form method="post" action="{% url 'emergency:create' %}">{% csrf_token %}{{ form.request_id }}
          {% for field in form %}{% if not field.is_hidden %}<div class="field-wrapper"><label class="form-label" for="{{ field.id_for_label }}">{{ field.label }}</label>{{ field }}{% if field.errors %}<ul class="field-errors" id="{{ field.auto_id }}_error">{% for error in field.errors %}<li>{{ error }}</li>{% endfor %}</ul>{% endif %}</div>{% endif %}{% endfor %}
          <button class="btn btn-primary" type="submit">Save entered location</button>
        </form>
      </details>
    </section>
    <aside class="account-panel" aria-labelledby="saved-heading"><p class="eyebrow">Your account only</p><h2 id="saved-heading">Recently saved</h2><p class="text-muted">If a connection fails after saving, check here before starting again.</p>
      <ul class="sos-recent-list">{% for item in recent_requests %}<li><a href="{% url 'emergency:detail' item.pk %}">{{ item.created_at|date:'d M Y, H:i' }} · {{ item.get_status_display }}</a></li>{% empty %}<li>No saved requests yet.</li>{% endfor %}</ul>
      <a class="back-link" href="{% url 'accounts:profile' %}">Review your emergency contacts {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</a>
    </aside>
  </div>
</div></section>
{% endblock %}
```

### `templates/emergency/detail.html`

Explicit manual sharing, message copying and eligible own contacts.

```html
{% extends 'base.html' %}
{% block title %}Share your SOS location | MEDTAP{% endblock %}
{% block content %}
<section class="account-section"><div class="container sos-page">
  <div class="sos-heading"><p class="eyebrow">Saved to your account</p><h1>Your request is saved.<br>Now share it.</h1><p>No one has been notified by MEDTAP. Choose how to reach your people below.</p></div>
  <div class="sos-critical-note"><strong>This app does not replace calling 112.</strong> No ambulance has been booked. <a href="tel:112">Call 112 for emergency assistance.</a></div>
  <div class="sos-layout">
    <section class="account-panel" aria-labelledby="message-heading">
      <h2 id="message-heading">A message ready to send</h2>
      <ol class="sos-timeline" aria-label="Sharing steps"><li class="sos-step-complete"><strong>Location recorded</strong><span>{{ emergency.created_at|date:'d M Y, H:i T' }} · {{ emergency.get_status_display }}</span></li><li><strong>Choose a contact or app</strong><span>Open a composer below, or copy the message.</span></li><li><strong>Press Send in that app</strong><span>MEDTAP cannot confirm delivery or a response.</span></li></ol>
      <label class="form-label" for="sos-message">Message (includes your recorded location)</label>
      <textarea id="sos-message" class="form-control sos-message" rows="8" readonly>{{ share_message }}</textarea>
      <div class="sos-share-actions"><button class="btn btn-primary" id="copy-sos-message" type="button" hidden>Copy message</button><a class="btn btn-outline-primary" href="{{ general_share.whatsapp_url }}" target="_blank" rel="noopener noreferrer">Choose in WhatsApp</a><a class="btn btn-outline-primary" href="{{ general_share.sms_url }}">Choose in SMS</a></div>
      <p id="copy-feedback" class="field-help" role="status" aria-live="polite">You can select and copy the message manually. SMS links need a compatible messaging app and may create multiple billable messages.</p>
      <p class="field-help">{{ emergency.latitude }}, {{ emergency.longitude }} · <a href="{{ maps_url }}" target="_blank" rel="noopener noreferrer">Open the recorded location in Google Maps</a></p>
      <p class="field-help">The snapshot does not update as you move. Opening a sharing link passes this message to the selected service; review its recipient and press Send yourself. Your medical profile is not included.</p>
    </section>
    <section class="account-panel" aria-labelledby="contact-heading"><p class="eyebrow">Reach someone you trust</p><h2 id="contact-heading">Your emergency contacts</h2>
      {% for row in contact_shares %}<article class="sos-contact"><div class="contact-heading"><h3>{{ row.contact.name }}</h3>{% if row.contact.is_primary %}<span class="primary-label">Primary contact</span>{% endif %}</div><p class="text-muted">{{ row.contact.relationship }} · {{ row.contact.phone }}</p>
        <div class="sos-share-actions">{% if row.options.whatsapp_url %}<a class="btn btn-outline-primary" href="{{ row.options.whatsapp_url }}" target="_blank" rel="noopener noreferrer" aria-label="Open WhatsApp message to {{ row.contact.name }}">WhatsApp</a>{% endif %}{% if row.options.sms_url %}<a class="btn btn-outline-primary" href="{{ row.options.sms_url }}" aria-label="Open SMS message to {{ row.contact.name }}">SMS</a>{% else %}<span class="field-help">This placeholder or invalid number cannot be used for sharing.</span>{% endif %}</div>
        {% if not row.options.whatsapp_url and row.options.sms_url %}<p class="field-help">For a direct WhatsApp link, update this contact with a +country-code number. You can also choose them using the general WhatsApp button.</p>{% endif %}
      </article>{% empty %}<p class="text-muted">No emergency contacts are saved. Use the general share buttons or copy the message for someone you trust.</p>{% endfor %}
      <a class="back-link" href="{% url 'accounts:profile' %}">Manage emergency contacts {% include 'partials/icon.html' with name='arrow-up-right' class_name='icon-sm' only %}</a>
    </section>
  </div>
</div></section>
{% endblock %}
```

### `templates/core/home.html`

Current home copy explains SOS saving and preserves live facility search.

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
        <p id="sos-preview-note">Call 112 for immediate emergency help. SOS saves your location so you can share it yourself. No ambulance is booked.</p>
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

### `templates/partials/footer.html`

The visible disclaimer explains the app's current limits.

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
        <p class="footer-disclaimer mb-0"><strong>This app does not replace calling 112.</strong> SOS saves a location for you to share manually. MEDTAP does not notify contacts or book an ambulance.</p>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; {% now 'Y' %} MEDTAP. Built with care.</span>
      <span>Medical Emergency App &middot; Student project</span>
    </div>
  </div>
</footer>
```

### `static/js/sos.js`

Fresh capture, busy states, same-ID retries and copy fallback without automatic sending.

```javascript
"use strict";

(() => {
  const form = document.getElementById("sos-request-form");
  if (form) {
    const triggers = document.querySelectorAll("[data-sos-trigger]");
    const feedback = document.getElementById("sos-feedback");
    const text = document.getElementById("sos-feedback-text");
    const spinner = document.getElementById("sos-spinner");
    const fallback = document.getElementById("sos-fallback");
    let busy = false;
    let requestId = null;

    function show(message, loading = false) {
      feedback.hidden = false;
      spinner.hidden = !loading;
      text.textContent = message;
      fallback.hidden = loading;
      triggers.forEach((trigger) => trigger.setAttribute("aria-disabled", String(loading)));
      feedback.focus();
    }

    function fail(message) {
      busy = false;
      show(message);
    }

    async function save(latitude, longitude) {
      const body = new FormData(form);
      body.set("request_id", requestId);
      body.set("latitude", latitude.toFixed(6));
      body.set("longitude", longitude.toFixed(6));
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 15000);
      show("Saving your location. No one is being contacted automatically.", true);
      try {
        const response = await fetch(form.action, {
          method: "POST", body, credentials: "same-origin",
          headers: { Accept: "application/json" }, signal: controller.signal,
        });
        if (!response.ok || response.redirected) throw new Error("Save unconfirmed");
        const data = await response.json();
        if (typeof data.url !== "string" || !/^\/emergency\/sos\/[0-9a-f-]+\/$/i.test(data.url)) {
          throw new Error("Invalid redirect");
        }
        window.location.assign(data.url);
      } catch {
        fail("We couldn't confirm saving. Check Recently saved on the SOS page, or tap SOS to retry. Retrying this button uses the same request ID.");
      } finally {
        clearTimeout(timer);
      }
    }

    triggers.forEach((trigger) => trigger.addEventListener("click", (event) => {
      // Preserve ordinary open-in-new-tab behavior; GET never creates a request.
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      if (busy) return;
      if (!window.isSecureContext || !navigator.geolocation || !window.crypto?.randomUUID) {
        fail("Automatic location capture is unavailable. Use the SOS page to enter coordinates, or call 112.");
        return;
      }
      busy = true;
      requestId = requestId || window.crypto.randomUUID();
      show("Finding your location. Your browser may ask for permission. For urgent help, call 112.", true);
      try {
        navigator.geolocation.getCurrentPosition((position) => {
          const { latitude, longitude } = position.coords;
          if (!Number.isFinite(latitude) || !Number.isFinite(longitude) ||
              Math.abs(latitude) > 90 || Math.abs(longitude) > 180) {
            fail("We couldn't read valid coordinates. Open the SOS page for manual entry or call 112.");
            return;
          }
          save(latitude, longitude);
        }, (error) => {
          const errors = {
            1: "Location permission was declined.",
            2: "Your location is unavailable right now.",
            3: "Finding your location took too long.",
          };
          fail((errors[error.code] || "Location capture failed.") + " Open the SOS page for manual entry, or call 112.");
        }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 });
      } catch {
        fail("Location capture failed. Open the SOS page for manual entry, or call 112.");
      }
    }));
  }

  const copyButton = document.getElementById("copy-sos-message");
  const message = document.getElementById("sos-message");
  const copyFeedback = document.getElementById("copy-feedback");
  if (copyButton && message) {
    copyButton.hidden = false;
    copyButton.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(message.value);
        copyFeedback.textContent = "Message copied. Paste it into your chosen app and send it yourself.";
      } catch {
        message.focus();
        message.select();
        copyFeedback.textContent = "Copy is unavailable. The message is selected; use your device's Copy command.";
      }
    });
  }
})();
```

### `static/css/theme.css`

Complete current theme: original home/accounts/finder styles plus responsive SOS components.

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
/* SOS capture and manual sharing: no implied dispatch or delivery status. */
.sos-button { text-decoration: none; }
.sos-button[aria-disabled='true'] { animation: none; opacity: .75; cursor: wait; }
.sos-page { max-width: 1100px; }
.sos-heading { margin-bottom: 1.6rem; }
.sos-heading h1 { font-size: clamp(2.1rem, 4vw, 3.2rem); letter-spacing: -.05em; }
.sos-heading > p:last-child { color: var(--muted); max-width: 42rem; }
.sos-critical-note { padding: 1rem 1.2rem; border-left: 4px solid var(--emergency); border-radius: .5rem; background: #FFF4F3; color: #7C2020; margin-bottom: 1.5rem; }
.sos-critical-note a { color: #7C2020; display: inline-flex; align-items: center; min-height: 44px; }
.sos-layout { display: grid; grid-template-columns: 1.2fr 1fr; gap: 1.5rem; align-items: start; }
.sos-start-panel > .sos-button { margin: 1.5rem 0; }
.sos-start-panel > p, .sos-contact p { color: var(--muted); }
.sos-manual-summary { min-height: 44px; padding-block: .6rem; color: var(--primary-dark); cursor: pointer; }
.sos-recent-list { padding-left: 1.1rem; color: var(--muted); }
.sos-recent-list a { display: inline-flex; align-items: center; min-height: 44px; }
.sos-timeline { list-style: none; padding-left: 1.4rem; margin: 1.5rem 0 2rem; border-left: 2px solid var(--border); }
.sos-timeline li { position: relative; padding: 0 0 1.3rem .35rem; }
.sos-timeline li:last-child { padding-bottom: 0; }
.sos-timeline li::before { content: ''; position: absolute; left: -1.85rem; top: .3rem; width: 12px; height: 12px; border-radius: 50%; border: 2px solid var(--muted); background: white; }
.sos-timeline .sos-step-complete::before { background: var(--accent-dark); border-color: var(--accent-dark); }
.sos-timeline strong { display: block; font-weight: 600; color: var(--ink); }
.sos-timeline span { display: block; color: var(--muted); font-size: .9rem; }
.sos-message { min-height: 260px; line-height: 1.7; padding: 1rem; font-size: 1rem; resize: vertical; }
.sos-share-actions { display: flex; flex-wrap: wrap; gap: .6rem; margin: 1rem 0; }
.sos-share-actions .btn { font-size: .9rem; }
.sos-contact { padding: 1.2rem 0; border-bottom: 1px solid var(--border); overflow-wrap: anywhere; }
.sos-contact .contact-heading h3 { font-size: 1.1rem; }
.sos-contact p { font-size: .9rem; margin: .4rem 0; }
.sos-feedback { position: fixed; top: 105px; right: 1rem; z-index: 1030; width: min(420px, calc(100% - 2rem)); border: 2px solid var(--primary-dark); border-radius: 1rem; padding: 1.2rem; color: var(--primary-dark); background: white; box-shadow: var(--shadow); }
.sos-feedback p { margin: .5rem 0 0; }
.sos-feedback a { display: inline-flex; align-items: center; min-height: 44px; margin-top: .6rem; }
@media (max-width: 767.98px) {
  .sos-layout { grid-template-columns: 1fr; }
  .sos-feedback { top: 88px; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

### `emergency/tests.py`

Django tests use an isolated test database and fictional contacts.

```python
import uuid
from decimal import Decimal
from urllib.parse import parse_qs, urlsplit

from django.core.exceptions import ValidationError
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from accounts.models import EmergencyContact, MedicalProfile, User

from .forms import EmergencyRequestForm
from .models import AmbulanceRequest, EmergencyRequest
from .services import build_emergency_message, build_share_options, google_maps_url


class ShareOptionsTests(SimpleTestCase):
    def test_generic_composers_url_encode_the_whole_message(self):
        message = "Help & location?\nhttps://example.invalid/?x=1&y=2 + café"
        options = build_share_options(message)
        self.assertEqual(parse_qs(urlsplit(options.whatsapp_url).query)["text"], [message])
        self.assertEqual(parse_qs(urlsplit(options.sms_url).query)["body"], [message])
        self.assertEqual(urlsplit(options.whatsapp_url).netloc, "wa.me")

    def test_international_number_has_direct_whatsapp_and_sms(self):
        # Fictional number used only in isolated tests; no request is sent.
        options = build_share_options("test", "+999000000001")
        self.assertEqual(options.whatsapp_url, "https://wa.me/999000000001?text=test")
        self.assertEqual(options.sms_url, "sms:+999000000001?body=test")

    def test_local_phone_does_not_guess_country_code(self):
        options = build_share_options("test", "0000000001")
        self.assertIsNone(options.whatsapp_url)
        self.assertEqual(options.sms_url, "sms:0000000001?body=test")

    def test_placeholder_and_unsafe_numbers_have_no_links(self):
        for phone in ("0000000000", "+0000000000", "", "123", "javascript:alert(1)", "12?body=bad", "+999000000001\n"):
            with self.subTest(phone=phone):
                self.assertEqual(build_share_options("test", phone).whatsapp_url, None)
                self.assertEqual(build_share_options("test", phone).sms_url, None)


class EmergencyFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="sos-test-owner")
        cls.other = User.objects.create_user(username="sos-test-other")
        cls.profile = MedicalProfile.objects.create(user=cls.user, allergies="PRIVATE ALLERGY", medical_conditions="PRIVATE CONDITION")
        cls.other_profile = MedicalProfile.objects.create(user=cls.other)
        cls.contact = EmergencyContact.objects.create(profile=cls.profile, name="FAKE Contact", relationship="Friend", phone="0000000000", is_primary=True)
        cls.foreign_contact = EmergencyContact.objects.create(profile=cls.other_profile, name="OTHER PRIVATE CONTACT", relationship="Friend", phone="0000000000")

    def setUp(self):
        self.client.force_login(self.user)

    def payload(self, **changes):
        data = {"request_id": str(uuid.uuid4()), "latitude": "12.970000", "longitude": "77.590000"}
        data.update(changes)
        return data

    def create_request(self, **changes):
        response = self.client.post(reverse("emergency:create"), self.payload(**changes))
        self.assertEqual(response.status_code, 302)
        return EmergencyRequest.objects.get(pk=response.url.rstrip("/").split("/")[-1])

    def test_anonymous_users_must_login_for_every_emergency_page(self):
        self.client.logout()
        for url in (reverse("emergency:start"), reverse("emergency:detail", args=[uuid.uuid4()])):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(reverse("accounts:login") + "?next="))
        self.assertEqual(EmergencyRequest.objects.count(), 0)

    def test_expired_login_returns_to_get_page_and_json_gets_401(self):
        self.client.logout()
        response = self.client.post(reverse("emergency:create"), self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(parse_qs(urlsplit(response.url).query)["next"], [reverse("emergency:start")])
        response = self.client.post(reverse("emergency:create"), self.payload(), HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(EmergencyRequest.objects.count(), 0)

    def test_get_start_never_creates_or_captures_location(self):
        response = self.client.get(reverse("emergency:start"))
        self.assertContains(response, "Saving here does not notify")
        self.assertContains(response, "sos-request-form")
        self.assertEqual(EmergencyRequest.objects.count(), 0)

    def test_create_is_post_only_and_detail_is_get_only(self):
        self.assertEqual(self.client.get(reverse("emergency:create")).status_code, 405)
        item = self.create_request()
        self.assertEqual(self.client.post(reverse("emergency:detail", args=[item.pk])).status_code, 405)

    def test_manual_post_saves_owned_active_request_and_redirects(self):
        item = self.create_request(latitude="0", longitude="0")
        self.assertEqual(item.user_id, self.user.pk)
        self.assertEqual(item.latitude, 0)
        self.assertEqual(item.longitude, 0)
        self.assertEqual(item.status, EmergencyRequest.Status.ACTIVE)
        self.assertEqual(AmbulanceRequest.objects.count(), 0)
        item.full_clean()

    def test_invalid_coordinates_and_uuid_do_not_save(self):
        for changes in ({"latitude": "91"}, {"longitude": "-181"}, {"latitude": "NaN"},
                        {"longitude": "Infinity"}, {"latitude": ""}, {"longitude": ""},
                        {"latitude": "12.1234567"}, {"request_id": "bad"}, {"request_id": ""}):
            with self.subTest(changes=changes):
                response = self.client.post(reverse("emergency:create"), self.payload(**changes))
                self.assertEqual(response.status_code, 400)
                self.assertContains(response, "Your request was not saved", status_code=400)
        self.assertEqual(EmergencyRequest.objects.count(), 0)

    def test_coordinate_boundaries_validate_in_form_and_model(self):
        for lat, lon in (("90", "180"), ("-90", "-180"), ("0", "0")):
            self.assertTrue(EmergencyRequestForm(self.payload(latitude=lat, longitude=lon)).is_valid())
        for lat, lon in (("91", "0"), ("0", "181")):
            with self.assertRaises(ValidationError):
                EmergencyRequest(user=self.user, latitude=Decimal(lat), longitude=Decimal(lon)).full_clean()

    def test_extra_fields_cannot_override_user_or_status(self):
        item = self.create_request(user=self.other.pk, status="resolved", operator_notes="bad")
        self.assertEqual(item.user_id, self.user.pk)
        self.assertEqual(item.status, "active")

    def test_retry_returns_same_request_without_overwriting_location_or_status(self):
        data = self.payload()
        self.client.post(reverse("emergency:create"), data)
        item = EmergencyRequest.objects.get()
        saved_at = item.created_at
        item.status = "resolved"
        item.save()
        data["latitude"] = "0"
        response = self.client.post(reverse("emergency:create"), data, HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["created"])
        self.assertEqual(EmergencyRequest.objects.count(), 1)
        item.refresh_from_db()
        self.assertEqual(item.latitude, Decimal("12.970000"))
        self.assertEqual(item.status, "resolved")
        self.assertEqual(item.created_at, saved_at)

    def test_json_create_returns_owned_detail_url(self):
        data = self.payload()
        response = self.client.post(reverse("emergency:create"), data, HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["created"])
        self.assertEqual(response.json()["url"], reverse("emergency:detail", args=[data["request_id"]]))

    def test_json_errors_are_field_errors(self):
        response = self.client.post(reverse("emergency:create"), self.payload(latitude="bad"), HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("latitude", response.json()["errors"])

    def test_other_users_cannot_read_a_request_even_with_its_uuid(self):
        item = self.create_request()
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("emergency:detail", args=[item.pk])).status_code, 404)

    def test_other_users_cannot_claim_a_request_id(self):
        item = self.create_request()
        self.client.force_login(self.other)
        response = self.client.post(reverse("emergency:create"), self.payload(request_id=str(item.pk)))
        self.assertEqual(response.status_code, 403)
        item.refresh_from_db()
        self.assertEqual(item.user_id, self.user.pk)
        self.assertEqual(EmergencyRequest.objects.count(), 1)

    def test_detail_only_includes_own_contacts_and_no_automatic_notification_claim(self):
        item = self.create_request()
        response = self.client.get(reverse("emergency:detail", args=[item.pk]))
        self.assertContains(response, "FAKE Contact")
        self.assertNotContains(response, "OTHER PRIVATE CONTACT")
        self.assertContains(response, "No one has been notified by MEDTAP")
        self.assertNotContains(response, "Ambulance assigned")
        self.assertNotContains(response, 'href="sms:0000000000')

    def test_message_contains_snapshot_timestamp_and_encoded_maps_link_but_no_medical_data(self):
        item = self.create_request()
        message = build_emergency_message(item)
        query = parse_qs(urlsplit(google_maps_url(item)).query)
        self.assertEqual(query, {"api": ["1"], "query": ["12.970000,77.590000"]})
        self.assertIn("not live tracking", message)
        self.assertIn("does not book an ambulance", message)
        self.assertIn("Saved:", message)
        self.assertNotIn("PRIVATE ALLERGY", message)
        self.assertNotIn("PRIVATE CONDITION", message)
        self.assertNotIn(str(item.pk), message)

    def test_recent_requests_are_own_only_and_bounded(self):
        for _ in range(6):
            self.create_request()
        EmergencyRequest.objects.create(user=self.other, latitude=0, longitude=0)
        response = self.client.get(reverse("emergency:start"))
        self.assertEqual(len(response.context["recent_requests"]), 5)
        self.assertTrue(all(item.user_id == self.user.pk for item in response.context["recent_requests"]))

    def test_private_responses_are_not_cacheable_and_do_not_leak_referrers(self):
        item = self.create_request()
        for url in (reverse("emergency:start"), reverse("emergency:detail", args=[item.pk])):
            response = self.client.get(url)
            self.assertIn("no-store", response["Cache-Control"])
            self.assertEqual(response["Referrer-Policy"], "same-origin")
        response = self.client.post(reverse("emergency:create"), self.payload(), HTTP_ACCEPT="application/json")
        self.assertIn("no-store", response["Cache-Control"])

    def test_csrf_is_required_even_for_json_accepting_requests(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        url = reverse("emergency:create")
        self.assertEqual(client.post(url, self.payload(), HTTP_ACCEPT="application/json").status_code, 403)
        client.get(reverse("emergency:start"))
        token = client.cookies["csrftoken"].value
        response = client.post(url, self.payload(csrfmiddlewaretoken=token), HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 201)

    def test_contact_html_is_escaped_and_primary_sorts_first(self):
        EmergencyContact.objects.create(profile=self.profile, name="<img src=x onerror=alert(1)>", relationship="Friend", phone="0000000000")
        item = self.create_request()
        response = self.client.get(reverse("emergency:detail", args=[item.pk]))
        self.assertContains(response, "&lt;img src=x onerror=alert(1)&gt;")
        self.assertNotContains(response, "<img src=x onerror=alert(1)>")
        self.assertEqual(response.context["contact_shares"][0]["contact"], self.contact)

    def test_deleted_owner_request_cannot_be_read_by_another_user(self):
        item = self.create_request()
        self.user.delete()
        item.refresh_from_db()
        self.assertIsNone(item.user_id)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("emergency:detail", args=[item.pk])).status_code, 404)

    def test_guest_sos_link_remains_usable_without_javascript(self):
        self.client.logout()
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'href="/emergency/sos/"')
        self.assertNotContains(response, 'id="sos-request-form"')
```

### `emergency/frontend_tests.cjs`

Node mocks exercise browser APIs without real location or messaging services.

```javascript
// Run with Node. Mocks never request real GPS, contact anybody, or send an SMS.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const code = fs.readFileSync(path.join(__dirname, "..", "static", "js", "sos.js"), "utf8");
const uuid = "00000000-0000-4000-8000-000000000001";
const detail = `/emergency/sos/${uuid}/`;
const settle = () => new Promise(setImmediate);

function element() {
  return { hidden: true, value: "message & location", textContent: "", attributes: {}, events: {},
    addEventListener(name, callback) { this.events[name] = callback; },
    setAttribute(name, value) { this.attributes[name] = value; },
    focus() { this.focused = true; }, select() { this.selected = true; },
  };
}
function fixture({ guest = false, secure = true, fetchImpl, clipboardFails = false } = {}) {
  const nodes = {};
  for (const id of ["sos-request-form", "sos-feedback", "sos-feedback-text", "sos-spinner", "sos-fallback", "copy-sos-message", "sos-message", "copy-feedback"]) nodes[id] = element();
  nodes["sos-request-form"].action = "/emergency/sos/create/";
  const triggers = [element(), element()];
  const captures = [], posts = [], navigations = [], copies = [];
  let idCalls = 0;
  class FakeFormData {
    constructor() { this.values = new Map([["csrfmiddlewaretoken", "isolated-test-token"]]); }
    set(key, value) { this.values.set(key, value); }
    get(key) { return this.values.get(key); }
  }
  vm.runInNewContext(code, {
    document: { getElementById: (id) => guest && id === "sos-request-form" ? null : nodes[id], querySelectorAll: () => triggers },
    window: { isSecureContext: secure, crypto: { randomUUID: () => { idCalls += 1; return uuid; } }, location: { assign: (url) => navigations.push(url) } },
    navigator: { geolocation: { getCurrentPosition: (ok, fail, options) => captures.push({ ok, fail, options }) },
      clipboard: { async writeText(text) { if (clipboardFails) throw Error("denied"); copies.push(text); } } },
    FormData: FakeFormData, AbortController, setTimeout, clearTimeout,
    fetch: async (url, options) => {
      posts.push({ url, options });
      if (fetchImpl) return fetchImpl();
      return { ok: true, redirected: false, json: async () => ({ url: detail, created: true }) };
    },
  });
  return { nodes, triggers, captures, posts, navigations, copies,
    click: (index = 0, event = {}) => triggers[index].events.click({ preventDefault() {}, ...event }),
    success: (lat = 0, lon = 77.59000012) => captures.at(-1).ok({ coords: { latitude: lat, longitude: lon } }),
    get idCalls() { return idCalls; },
  };
}

(async () => {
  let count = 0;
  async function test(name, run) { await run(); count += 1; console.log(`PASS ${name}`); }
  await test("guest links keep their normal login destination", () => {
    const state = fixture({ guest: true });
    assert.equal(state.triggers[0].events.click, undefined);
    assert.equal(state.captures.length, 0);
  });
  await test("capture starts on a tap only and duplicate desktop/mobile taps are ignored", () => {
    const state = fixture();
    assert.equal(state.captures.length, 0);
    state.click(0); state.click(1);
    assert.equal(state.captures.length, 1);
    assert.equal(state.captures[0].options.timeout, 10000);
    assert.equal(state.captures[0].options.maximumAge, 0);
    assert.equal(state.nodes["sos-spinner"].hidden, false);
    assert.equal(state.triggers[1].attributes["aria-disabled"], "true");
  });
  await test("a successful capture includes CSRF, rounds coordinates and navigates to the owned result", async () => {
    const state = fixture(); state.click(); state.success(); await settle();
    assert.equal(state.posts.length, 1);
    const options = state.posts[0].options;
    assert.equal(options.method, "POST");
    assert.equal(options.body.get("csrfmiddlewaretoken"), "isolated-test-token");
    assert.equal(options.body.get("latitude"), "0.000000");
    assert.equal(options.body.get("longitude"), "77.590000");
    assert.equal(options.body.get("request_id"), uuid);
    assert.deepEqual(state.navigations, [detail]);
  });
  await test("denial, unavailability and timeout reveal the manual fallback without posting", () => {
    for (const errorCode of [1, 2, 3, 99]) {
      const state = fixture(); state.click(); state.captures[0].fail({ code: errorCode });
      assert.equal(state.posts.length, 0);
      assert.equal(state.nodes["sos-spinner"].hidden, true);
      assert.equal(state.nodes["sos-fallback"].hidden, false);
      assert.match(state.nodes["sos-feedback-text"].textContent, /manual entry/);
    }
  });
  await test("nonfinite and out-of-range fixes never reach the server", () => {
    for (const [lat, lon] of [[NaN, 0], [0, Infinity], [91, 0], [0, -181]]) {
      const state = fixture(); state.click(); state.success(lat, lon);
      assert.equal(state.posts.length, 0);
      assert.match(state.nodes["sos-feedback-text"].textContent, /valid coordinates/);
    }
  });
  await test("an uncertain network save keeps the UUID for a safe retry", async () => {
    let attempt = 0;
    const state = fixture({ fetchImpl: () => {
      attempt += 1;
      if (attempt === 1) throw Error("offline");
      return { ok: true, redirected: false, json: async () => ({ url: detail }) };
    } });
    state.click(); state.success(); await settle();
    assert.match(state.nodes["sos-feedback-text"].textContent, /couldn't confirm/);
    state.click(); state.success(); await settle();
    assert.equal(state.posts.length, 2);
    assert.equal(state.posts[0].options.body.get("request_id"), state.posts[1].options.body.get("request_id"));
    assert.equal(state.idCalls, 1);
    assert.deepEqual(state.navigations, [detail]);
  });
  await test("expired login and non-success responses never pretend a save succeeded", async () => {
    for (const response of [{ ok: false }, { ok: true, redirected: true }]) {
      const state = fixture({ fetchImpl: () => response });
      state.click(); state.success(); await settle();
      assert.equal(state.navigations.length, 0);
      assert.match(state.nodes["sos-feedback-text"].textContent, /Recently saved/);
    }
  });
  await test("untrusted redirect URLs cannot navigate away", async () => {
    const state = fixture({ fetchImpl: () => ({ ok: true, json: async () => ({ url: "https://example.invalid/" }) }) });
    state.click(); state.success(); await settle();
    assert.equal(state.navigations.length, 0);
  });
  await test("insecure contexts and modified clicks do not capture GPS", () => {
    const state = fixture({ secure: false }); state.click();
    assert.equal(state.captures.length, 0);
    assert.match(state.nodes["sos-feedback-text"].textContent, /Automatic location capture is unavailable/);
    const modified = fixture(); modified.click(0, { ctrlKey: true });
    assert.equal(modified.captures.length, 0);
  });
  await test("copying only writes the message to the clipboard", async () => {
    const state = fixture(); await state.nodes["copy-sos-message"].events.click();
    assert.deepEqual(state.copies, [state.nodes["sos-message"].value]);
    assert.equal(state.posts.length, 0);
    assert.match(state.nodes["copy-feedback"].textContent, /send it yourself/);
  });
  await test("clipboard denial selects the message and explains manual copy", async () => {
    const state = fixture({ clipboardFails: true }); await state.nodes["copy-sos-message"].events.click();
    assert.equal(state.nodes["sos-message"].selected, true);
    assert.match(state.nodes["copy-feedback"].textContent, /Copy command/);
  });
  console.log(`${count} SOS frontend checks passed.`);
})().catch((error) => { console.error(error); process.exitCode = 1; });
```

### `facilities/test_nearby.py`

The existing search tests now expect current SOS home wording.

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
        self.assertContains(response, "SOS saves your location so you can share it yourself. No ambulance is booked.")
```

Stop here. Say **"next"** when you are ready for ambulance requests and operator status updates.
