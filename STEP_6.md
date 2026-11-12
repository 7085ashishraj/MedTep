# Step 6 — Ambulance requests and operator status updates

This feature is implemented in your workspace. Complete Steps 1–5 first. This
guide contains complete current source files, the migration, terminal commands
and viva notes. Older guides preserve their step's code; use the files here for
the current shared templates, forms, models, navigation and theme.

## What works now

- A signed-in user chooses a saved SOS location, reviews it and submits one
  ambulance request per SOS record through a CSRF-protected POST.
- The private owner page shows Requested → Accepted → On the way → Completed,
  with recorded transition timestamps and a reference facility when selected.
- Authorised operators have a paginated/filterable queue and a validated update
  form. They may keep the current status or advance exactly one step.
- Status changes record the actor/time. A version check rejects stale edits,
  including edits to notes or facility references.
- The owner page polls a private read-only status endpoint every 10 seconds while
  visible, with manual refresh available. Checks stop on completion or an error.
- Internal notes stay on operator pages, and FAKE facility references remain
  labelled. No medical profile or emergency-contact list is shown to operators.

**This is a project workflow, not a connected ambulance dispatch service.** No
provider is contacted, no real ambulance is confirmed, and no driver/GPS/ETA is
tracked. The visible notice says to call 112 in a real emergency. The four status
labels represent operator reports in this project, not independently verified
real-world progress. SOS sharing remains a separate manual action.

## Folder changes

```text
MEDTAP/
├── emergency/
│   ├── models.py                       # request version + status event model
│   ├── permissions.py                  # staff + explicit view/change permissions
│   ├── ambulance_services.py           # workflow, conditional writes, snapshots
│   ├── ambulance_views.py              # owner and operator function-based views
│   ├── forms.py                        # existing SOS + new operator/filter forms
│   ├── views.py                        # existing SOS now links transport workflow
│   ├── urls.py
│   ├── migrations/
│   │   └── 0002_ambulancerequest_version_ambulancestatusevent.py
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── setup_ambulance_operators.py
│   ├── test_ambulance.py                # 31 new Django tests
│   └── ambulance_frontend_tests.cjs     # 8 new JavaScript checks
├── core/views.py                       # live Ambulance quick action
├── templates/
│   ├── emergency/
│   │   ├── detail.html                 # existing SOS page links request/status
│   │   ├── ambulance_start.html
│   │   ├── ambulance_request.html
│   │   ├── ambulance_detail.html
│   │   ├── operator_dashboard.html
│   │   └── operator_update.html
│   └── partials/
│       ├── ambulance_notice.html
│       ├── form_fields.html            # correctly renders hidden fields
│       ├── navbar.html
│       └── footer.html
└── static/
    ├── css/theme.css
    └── js/ambulance.js
```

No new Python package, secret, external account or API key is required. Models
still use SQLite-compatible fields. Facility references are optional and only
active hospitals/clinics may be newly selected. An existing reference may be kept
if it later becomes inactive; it remains a reference, not a booking.

## Exact terminal commands — PowerShell

Run from MEDTAP in VS Code:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py setup_ambulance_operators
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test emergency accounts facilities
node emergency/ambulance_frontend_tests.cjs
node emergency/frontend_tests.cjs
node facilities/frontend_tests.cjs
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

The new migration is already applied in your workspace, and the operator group
already exists. Repeating the commands is safe. Expect **141 Django tests** and
**28 JavaScript checks** (8 ambulance + 11 SOS + 9 facilities) to pass. No new SOS
or ambulance records were inserted into your real database during visual review.
Node is needed only for the isolated frontend checks. Use your existing server
if one is running; stop it with Ctrl+C before starting a second on the same port.

To check migration state:

```powershell
.\.venv\Scripts\python.exe manage.py showmigrations emergency
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

Expect both emergency migrations marked `[X]` and `No changes detected`. The
migration adds `AmbulanceRequest.version` and creates `AmbulanceStatusEvent`;
existing request rows are retained. It does not invent historical timestamps.

## Set up an operator — no passwords in code

An existing active superuser with Staff status can use the operator dashboard.
If you do not have an admin account yet, create one interactively:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

For a separate operator account:

1. Register a separate ordinary user through the normal registration page.
2. Sign into [Django admin](http://127.0.0.1:8000/admin/) as a superuser.
3. Open **Accounts → Users**, choose that user, enable **Staff status** and add
   the **Ambulance operators** group. Save the user.
4. Sign into the normal website as that operator. Open
   [Operator queue](http://127.0.0.1:8000/emergency/operators/ambulances/).

The setup command creates the group and adds `view_ambulancerequest` and
`change_ambulancerequest`; it assigns no users and promotes nobody. It preserves
any permissions already present on a pre-existing group. The dashboard requires
an active signed-in staff user with both permissions. Staff alone, a regular
user with permissions but no staff flag, and view-only staff are rejected with
403. Guests must sign in first. Operators do not need permissions to edit medical
profiles, users or facilities. Use the custom queue for updates; ambulance models
are not registered as editable Django admin pages that bypass this workflow.

## End-to-end walkthrough

1. As an ordinary user, open [SOS](http://127.0.0.1:8000/emergency/sos/) and save a
   location when you intend to do so. For a learning-only test, use manual demo
   coordinates `12.970000, 77.590000`; this deliberately creates a local test
   record. It contacts no provider.
2. Follow **Start project ambulance request** from the saved SOS screen, or open
   [Your transport requests](http://127.0.0.1:8000/emergency/ambulance/). The list
   shows your ten newest saved SOS records. Older ones remain reachable through
   their own SOS detail page.
3. Review the snapshot/time and choose **Create project ambulance request**.
   Expect a private Requested progress page. Refreshing or repeating the same
   submission returns the existing request, including after it completes.
4. In a different browser/session as an operator, open the queue. Its default
   filter is open requests. Summary counts cover all requests, independently of
   the current filter. The queue contains up to 25 rows per page.
5. Choose **Review & update**, select Accepted, optionally choose a reference
   hospital/clinic and enter internal notes. Choose **Save project update**.
   The history shows that transition's actor and timestamp. The FAKE facilities
   are learning references only; none represents a real provider.
6. On the user's progress page, wait for the next visible-page check or choose
   **Refresh status**. It should show Accepted and the selected reference without
   exposing internal notes or operator usernames. A hidden tab pauses requests
   and checks again when visible.
7. Advance On the way, then Completed from the operator form. Skips/backward moves
   are rejected. The owner page stops automatic checks at Completed. A manual
   refresh still works if a completed record's reference is later corrected.
8. To demonstrate a conflict, open the operator form twice. Save one copy, then
   submit the older copy. Expect HTTP 409 with **Reload the latest version before
   saving**. Reload and review instead of overwriting the newer edit.

New transport requests require an active SOS record. An existing request can
always be reopened for viewing. Ambulance completion does not automatically
resolve the SOS record: these are separate lifecycles. There is no cancellation
or request re-opening flow in this step; a new SOS record can start a new request.
Internal note/facility edits may keep the current status, including Completed.

## Routes and data boundaries

| Route | Methods | Access / purpose |
| --- | --- | --- |
| `/emergency/ambulance/` | GET | Owner's recent SOS locations and request links |
| `/emergency/ambulance/request/<sos-uuid>/` | GET, POST | Owner's review and idempotent creation |
| `/emergency/ambulance/<id>/` | GET | Owner-only progress page |
| `/emergency/ambulance/<id>/status/` | GET | Owner-only JSON status snapshot |
| `/emergency/operators/ambulances/` | GET | Authorised operator queue |
| `/emergency/operators/ambulances/<id>/` | GET, POST | Authorised validated update |

Creation and operator writes use CSRF. GETs and polling do not change status or
create requests. All private views use no-store; external Maps links suppress
the private page's Referer. Known integer IDs/UUIDs do not grant access. An owner
query includes `emergency__user=request.user`, so another user's page or JSON
endpoint returns 404. Operator checks occur server-side before displaying queue
data; hiding a navigation link is only a usability improvement.

JSON keys are ID, status/label, version, updated timestamp, reference facility
name/demo flag and four timeline steps with recorded timestamps. It does not
contain internal notes, contact data, medical details or operator identities.
The endpoint currently uses the normal Django session, matching the website;
a later mobile client will need an appropriate authentication design.

## Viva notes

**One-to-one and idempotency.** AmbulanceRequest already has a one-to-one relation
to EmergencyRequest. Creation checks ownership and SOS status, then uses
`get_or_create` inside an atomic transaction. The request and initial Requested
event commit together. Repeating the action returns the same request; it does
not reset its status or add another Requested event.

**A state machine.** The ordered status list defines the current and next valid
choices. Forms offer those choices, and the service validates again. This is
business validation, not a client-only dropdown restriction. Keeping a status
for a notes/reference edit does not create a fictitious transition event.

**Optimistic concurrency.** Each edit submits a hidden expected version. Saving
uses a conditional SQL update of `WHERE id = ... AND version = ...`, incrementing
the stored version with `F()`. If no row matches, someone changed it first and
the edit is rejected as stale. The status change and its event occur inside the
same atomic transaction. If event insertion fails, the status/version update is
rolled back too. Notes/reference edits increment the version as well, so two
operators cannot silently overwrite each other's notes through this UI.

The create service also uses `select_for_update` where the database supports it.
[Django's QuerySet documentation](https://docs.djangoproject.com/en/6.1/ref/models/querysets/#select-for-update)
explains that SQLite does not provide that row lock. The unique one-to-one key and
conditional version write remain important safeguards. SQLite is suitable for
this learning project but can raise lock errors under concurrent writers; use
PostgreSQL and test actual concurrent load before real multi-operator deployment.
The tests exercise stale versions and a simulated failed conditional write, not
a production stress test. Direct SQL/shell writes bypass these service rules.

**Audit history.** Events record status, actor and time, with a unique constraint
on request/status because this workflow only moves forward. Deleting an operator
keeps the event with a null actor. Deleting a reference facility keeps the request
with a null reference. Old requests without events display **Timestamp not
recorded** instead of fabricated historical dates. Internal notes are not an
append-only audit log; only status transitions have event records in this step.

**Polling as progressive enhancement.** The template renders a usable initial
timeline. JavaScript reads only the current owner's status snapshot, uses text
nodes for facility names, and updates the timeline/ARIA state. A ten-second timer
runs only while visible; fetches have a timeout and do not overlap. An error or
expired login pauses checks and explains that the last displayed status may be
out of date. Manual Refresh status works without JavaScript. This is periodic
status reporting, not live vehicle tracking or delivery confirmation.

For framework background, see [Django transactions](https://docs.djangoproject.com/en/6.1/topics/db/transactions/)
and [Django permissions](https://docs.djangoproject.com/en/6.1/topics/auth/default/#permissions-and-authorization).
The custom role check combines Django permissions with active/staff requirements.

## Verification completed

- **141 Django tests:** previous 110 plus 31 ambulance tests. Coverage includes
  owner/role boundaries, CSRF, idempotent creation, valid transitions, stale form
  conflicts, conditional-write failure, transaction rollback, reference validation,
  private notes, legacy history, pagination and repeatable group setup.
- **28 isolated JavaScript checks:** 8 ambulance, 11 SOS, 9 facilities. New checks
  cover delayed read-only polling, hidden tabs, timeline updates, completion,
  network/login failures and safe facility-name insertion.
- System checks and migration-drift checks pass, and the new migration is applied.
- Browser review in a separate fictional database confirmed review → creation →
  operator acceptance → automatic owner-page update, including the reference
  facility label and absence of internal notes on the owner page. Phone content
  has no horizontal overflow. The tablet operator navigation/form also fits.
- No user was promoted or assigned to the real operator group, no real transport
  record was created for the visual test, and no external provider was contacted.
  The isolated visual-test server was stopped afterwards.

## Complete source files

Create parent folders where needed. Replace each file below in full. The two
`__init__.py` package markers are intentionally empty. Keep the existing settings,
base template, SOS service/script, accounts and facilities files from earlier steps.

### `emergency/models.py`

Existing models plus optimistic versioning and a status event model.

```python
import uuid

from django.conf import settings
from django.db import models

from common.models import TimeStampedModel
from common.validators import latitude_validators, longitude_validators


class EmergencyRequest(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RESOLVED = "resolved", "Resolved"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emergency_requests",
    )
    latitude = models.DecimalField(
        max_digits=8, decimal_places=6, validators=latitude_validators,
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, validators=longitude_validators,
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE,
    )

    class Meta:
        ordering = ["-created_at", "pk"]
        indexes = [models.Index(fields=["status", "created_at"])]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    latitude__gte=-90, latitude__lte=90,
                    longitude__gte=-180, longitude__lte=180,
                ),
                name="emergency_valid_coordinates",
            ),
        ]

    def __str__(self):
        return f"SOS {self.pk} ({self.get_status_display()})"


class AmbulanceRequest(TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        ACCEPTED = "accepted", "Accepted"
        ON_THE_WAY = "on_the_way", "On the way"
        COMPLETED = "completed", "Completed"

    emergency = models.OneToOneField(
        EmergencyRequest, on_delete=models.CASCADE, related_name="ambulance_request",
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ambulance_requests",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.REQUESTED,
    )
    operator_notes = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ["-created_at", "pk"]
        indexes = [models.Index(fields=["status", "created_at"])]

    def __str__(self):
        return f"Ambulance for {self.emergency_id} ({self.get_status_display()})"


class AmbulanceStatusEvent(models.Model):
    ambulance = models.ForeignKey(
        AmbulanceRequest, on_delete=models.CASCADE, related_name="status_events",
    )
    status = models.CharField(max_length=20, choices=AmbulanceRequest.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="ambulance_status_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]
        constraints = [models.UniqueConstraint(
            fields=["ambulance", "status"], name="one_ambulance_event_per_status",
        )]

    def __str__(self):
        return f"{self.ambulance_id}: {self.get_status_display()}"
```

### `emergency/permissions.py`

One server-side operator access check shared by views and services.

```python
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

OPERATOR_PERMISSIONS = (
    "emergency.view_ambulancerequest", "emergency.change_ambulancerequest",
)


def can_operate(user):
    return user.is_authenticated and user.is_active and user.is_staff and user.has_perms(OPERATOR_PERMISSIONS)


def operator_required(view):
    @wraps(view)
    @login_required
    def checked(request, *args, **kwargs):
        if not can_operate(request.user):
            raise PermissionDenied("This dashboard requires an authorised ambulance operator.")
        return view(request, *args, **kwargs)
    return checked
```

### `emergency/ambulance_services.py`

Atomic workflow operations and a public-to-the-owner status snapshot.

```python
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone

from facilities.models import Facility

from .models import AmbulanceRequest, AmbulanceStatusEvent, EmergencyRequest
from .permissions import can_operate

STATUS_ORDER = list(AmbulanceRequest.Status.values)


def allowed_statuses(current):
    index = STATUS_ORDER.index(current)
    return STATUS_ORDER[index:index + 2]


@transaction.atomic
def request_ambulance(*, user, emergency_pk):
    emergency = get_object_or_404(EmergencyRequest.objects.select_for_update(), pk=emergency_pk, user=user)
    existing = AmbulanceRequest.objects.filter(emergency=emergency).first()
    if existing:
        return existing, False
    if emergency.status != EmergencyRequest.Status.ACTIVE:
        raise ValidationError("Only an active SOS record can start a new ambulance request.")
    ambulance, created = AmbulanceRequest.objects.get_or_create(emergency=emergency)
    if created:
        AmbulanceStatusEvent.objects.create(
            ambulance=ambulance, status=ambulance.status, changed_by=user,
        )
    return ambulance, created


@transaction.atomic
def update_ambulance(*, operator, pk, expected_version, status, facility, operator_notes):
    if not can_operate(operator):
        raise PermissionDenied("Operator access is required.")
    ambulance = get_object_or_404(AmbulanceRequest, pk=pk)
    if ambulance.version != expected_version:
        raise ValidationError("Another operator changed this request. Reload the latest version before saving.", code="stale")
    if status not in allowed_statuses(ambulance.status):
        raise ValidationError("Move one step forward at a time; completed requests cannot be reopened.")
    if len(operator_notes) > 2000:
        raise ValidationError("Keep internal notes within 2000 characters.")
    if facility and facility.pk != ambulance.facility_id:
        # Re-check at save time in case the directory changed after form validation.
        facility = get_object_or_404(Facility, pk=facility.pk)
        if not facility.is_active or facility.facility_type not in (Facility.Type.HOSPITAL, Facility.Type.CLINIC):
            raise ValidationError("Choose an active hospital or clinic as the facility reference.")
    changed = AmbulanceRequest.objects.filter(pk=pk, version=expected_version).update(
        status=status, facility=facility, operator_notes=operator_notes,
        version=F("version") + 1, updated_at=timezone.now(),
    )
    if changed != 1:
        raise ValidationError("Another operator changed this request. Reload before saving.", code="stale")
    if status != ambulance.status:
        AmbulanceStatusEvent.objects.create(ambulance=ambulance, status=status, changed_by=operator)
    ambulance.refresh_from_db()
    return ambulance


def ambulance_snapshot(ambulance):
    events = {event.status: event.created_at for event in ambulance.status_events.all()}
    current = STATUS_ORDER.index(ambulance.status)
    return {
        "id": ambulance.pk, "status": ambulance.status,
        "status_label": ambulance.get_status_display(), "version": ambulance.version,
        "updated_at": ambulance.updated_at,
        "facility": {"name": ambulance.facility.name, "is_demo": ambulance.facility.is_demo} if ambulance.facility_id else None,
        "timeline": [{
            "status": value, "label": label, "is_current": index == current,
            "is_reached": index <= current, "recorded_at": events.get(value),
        } for index, (value, label) in enumerate(AmbulanceRequest.Status.choices)],
    }
```

### `emergency/forms.py`

Complete forms: SOS, eligible reference facilities, operator edits and queue filter.

```python
import uuid

from django import forms
from django.db.models import Q

from facilities.models import Facility

from .ambulance_services import allowed_statuses
from .models import AmbulanceRequest


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


class ReferenceFacilityField(forms.ModelChoiceField):
    def label_from_instance(self, facility):
        return facility.name + (" · FAKE sample" if facility.is_demo else "") + (" · inactive" if not facility.is_active else "")


class AmbulanceOperatorForm(forms.Form):
    expected_version = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    status = forms.ChoiceField(choices=AmbulanceRequest.Status.choices)
    facility = ReferenceFacilityField(
        queryset=Facility.objects.none(), required=False, label="Reference facility",
        help_text="A directory reference only; selecting it does not contact a provider.",
    )
    operator_notes = forms.CharField(
        required=False, max_length=2000, label="Internal operator notes",
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Visible only to authorised operators. Do not enter medical-profile details.",
    )

    def __init__(self, *args, ambulance, **kwargs):
        kwargs.setdefault("initial", {
            "expected_version": ambulance.version, "status": ambulance.status,
            "facility": ambulance.facility_id, "operator_notes": ambulance.operator_notes,
        })
        super().__init__(*args, **kwargs)
        choices = allowed_statuses(ambulance.status)
        self.fields["status"].choices = [(value, label) for value, label in AmbulanceRequest.Status.choices if value in choices]
        eligible = Q(is_active=True, facility_type__in=[Facility.Type.HOSPITAL, Facility.Type.CLINIC])
        self.fields["facility"].queryset = Facility.objects.filter(eligible | Q(pk=ambulance.facility_id))
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"


class AmbulanceDashboardForm(forms.Form):
    status = forms.ChoiceField(
        required=False,
        choices=[("open", "Open requests"), ("all", "All requests"), *AmbulanceRequest.Status.choices],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    page = forms.IntegerField(required=False, min_value=1, widget=forms.HiddenInput)
```

### `emergency/ambulance_views.py`

Consistent function-based owner/operator views with CSRF and ownership checks.

```python
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ValidationError
from django.core.paginator import InvalidPage, Paginator
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_GET, require_http_methods

from .ambulance_services import ambulance_snapshot, request_ambulance, update_ambulance
from .forms import AmbulanceDashboardForm, AmbulanceOperatorForm
from .models import AmbulanceRequest, EmergencyRequest
from .permissions import operator_required
from .services import google_maps_url


@never_cache
@login_required
@require_GET
def start(request):
    return render(request, "emergency/ambulance_start.html", {
        "locations": EmergencyRequest.objects.filter(user=request.user).select_related("ambulance_request")[:10],
    })


@never_cache
@require_http_methods(["GET", "POST"])
def request_transport(request, pk):
    if not request.user.is_authenticated:
        return redirect_to_login(request.path, login_url=reverse("accounts:login"))
    emergency = get_object_or_404(EmergencyRequest, pk=pk, user=request.user)
    existing = AmbulanceRequest.objects.filter(emergency=emergency).first()
    if existing:
        return redirect("emergency:ambulance_detail", pk=existing.pk)
    error = None
    if request.method == "POST":
        try:
            ambulance, _ = request_ambulance(user=request.user, emergency_pk=pk)
        except ValidationError as exc:
            error = " ".join(exc.messages)
        else:
            return redirect("emergency:ambulance_detail", pk=ambulance.pk)
    return render(request, "emergency/ambulance_request.html", {
        "emergency": emergency, "maps_url": google_maps_url(emergency), "error": error,
        "can_request": emergency.status == EmergencyRequest.Status.ACTIVE,
    }, status=400 if error else 200)


def owned_ambulance(request, pk):
    return get_object_or_404(
        AmbulanceRequest.objects.select_related("emergency", "facility").prefetch_related("status_events"),
        pk=pk, emergency__user=request.user,
    )


@never_cache
@login_required
@require_GET
def detail(request, pk):
    ambulance = owned_ambulance(request, pk)
    return render(request, "emergency/ambulance_detail.html", {
        "ambulance": ambulance, "snapshot": ambulance_snapshot(ambulance),
        "maps_url": google_maps_url(ambulance.emergency),
    })


@never_cache
@login_required
@require_GET
def status(request, pk):
    return JsonResponse(ambulance_snapshot(owned_ambulance(request, pk)))


@never_cache
@operator_required
@require_GET
def dashboard(request):
    form = AmbulanceDashboardForm(request.GET)
    rows = AmbulanceRequest.objects.select_related("emergency__user", "facility")
    counts = rows.aggregate(
        requested=Count("pk", filter=Q(status="requested")),
        progressing=Count("pk", filter=Q(status__in=["accepted", "on_the_way"])),
        completed=Count("pk", filter=Q(status="completed")),
    )
    page = None
    if form.is_valid():
        chosen = form.cleaned_data["status"] or "open"
        if chosen == "open":
            rows = rows.exclude(status="completed")
        elif chosen != "all":
            rows = rows.filter(status=chosen)
        try:
            page = Paginator(rows, 25).page(form.cleaned_data["page"] or 1)
        except InvalidPage as exc:
            raise Http404("That queue page does not exist.") from exc
    def page_query(number):
        params = request.GET.copy()
        params["page"] = number
        return "?" + params.urlencode()
    return render(request, "emergency/operator_dashboard.html", {
        "form": form, "page_obj": page, "counts": counts,
        "previous_query": page_query(page.previous_page_number()) if page and page.has_previous() else None,
        "next_query": page_query(page.next_page_number()) if page and page.has_next() else None,
    }, status=400 if form.errors else 200)


@sensitive_post_parameters()
@never_cache
@operator_required
@require_http_methods(["GET", "POST"])
def operator_update(request, pk):
    ambulance = get_object_or_404(
        AmbulanceRequest.objects.select_related("emergency__user", "facility").prefetch_related("status_events__changed_by"), pk=pk,
    )
    form = AmbulanceOperatorForm(request.POST if request.method == "POST" else None, ambulance=ambulance)
    code = 200
    if request.method == "POST":
        valid = form.is_valid()
        if form.cleaned_data.get("expected_version") is not None and form.cleaned_data["expected_version"] != ambulance.version:
            form.add_error(None, "Another operator changed this request. Reload the latest version before saving.")
            code = 409
        elif valid:
            try:
                update_ambulance(operator=request.user, pk=pk, **form.cleaned_data)
            except ValidationError as exc:
                form.add_error(None, exc)
                code = 409 if exc.code == "stale" else 400
            else:
                messages.success(request, "Project request updated. No external provider has been contacted.")
                return redirect("emergency:operator_update", pk=pk)
        else:
            code = 400
    return render(request, "emergency/operator_update.html", {
        "ambulance": ambulance, "form": form,
        "maps_url": google_maps_url(ambulance.emergency),
    }, status=code)
```

### `emergency/views.py`

The existing SOS detail now offers a transport request/status link.

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
from .models import AmbulanceRequest, EmergencyRequest
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
        "ambulance": AmbulanceRequest.objects.filter(emergency=emergency).first(),
        "maps_url": google_maps_url(emergency),
        "general_share": build_share_options(message),
        "contact_shares": [{"contact": contact, "options": build_share_options(message, contact.phone)} for contact in contacts],
    })
```

### `emergency/urls.py`

All current SOS and ambulance routes under the existing emergency prefix.

```python
from django.urls import path

from . import ambulance_views, views

app_name = "emergency"
urlpatterns = [
    path("sos/", views.start, name="start"),
    path("sos/create/", views.create, name="create"),
    path("sos/<uuid:pk>/", views.detail, name="detail"),
    path("ambulance/", ambulance_views.start, name="ambulance_start"),
    path("ambulance/request/<uuid:pk>/", ambulance_views.request_transport, name="ambulance_request"),
    path("ambulance/<int:pk>/", ambulance_views.detail, name="ambulance_detail"),
    path("ambulance/<int:pk>/status/", ambulance_views.status, name="ambulance_status"),
    path("operators/ambulances/", ambulance_views.dashboard, name="operator_dashboard"),
    path("operators/ambulances/<int:pk>/", ambulance_views.operator_update, name="operator_update"),
]
```

### `emergency/migrations/0002_ambulancerequest_version_ambulancestatusevent.py`

The complete generated schema migration; no invented historical events.

```python
# Generated by Django 6.1.3 on 2026-11-12 13:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emergency', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='ambulancerequest',
            name='version',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.CreateModel(
            name='AmbulanceStatusEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('requested', 'Requested'), ('accepted', 'Accepted'), ('on_the_way', 'On the way'), ('completed', 'Completed')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ambulance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_events', to='emergency.ambulancerequest')),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ambulance_status_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at', 'pk'],
                'constraints': [models.UniqueConstraint(fields=('ambulance', 'status'), name='one_ambulance_event_per_status')],
            },
        ),
    ]
```

### `emergency/management/__init__.py`

Empty Python package marker.

```python

```

### `emergency/management/commands/__init__.py`

Empty command-package marker.

```python

```

### `emergency/management/commands/setup_ambulance_operators.py`

Repeatable role-group setup without assigning or promoting a user.

```python
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the operator group with view/change ambulance permissions; assign no users."
    requires_migrations_checks = True

    def handle(self, *args, **options):
        permissions = Permission.objects.filter(
            content_type__app_label="emergency", content_type__model="ambulancerequest",
            codename__in=["view_ambulancerequest", "change_ambulancerequest"],
        )
        if permissions.count() != 2:
            raise CommandError("Run migrate first to create the required model permissions.")
        group, _ = Group.objects.get_or_create(name="Ambulance operators")
        group.permissions.add(*permissions)
        self.stdout.write(self.style.SUCCESS(
            "Operator group is ready. No users were assigned or promoted.\n"
            "In admin, add your chosen user to Ambulance operators and enable Staff status."
        ))
```

### `core/views.py`

The Ambulance home action opens the real project workflow.

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
            "href": reverse("emergency:ambulance_start"), "status": "Project request & status",
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

### `templates/partials/ambulance_notice.html`

The shared visible notice distinguishes project statuses from real dispatch.

```html
<div class="sos-critical-note"><strong>Project workflow — no dispatch service is connected.</strong> These are manually reported project statuses, not confirmation of a real ambulance. This app does not replace calling 112. <a href="tel:112">Call 112 for emergency assistance.</a></div>
```

### `templates/partials/form_fields.html`

The reusable form renderer keeps hidden version inputs out of the visible UI.

```html
{% for field in form %}
{% if field.is_hidden %}{{ field }}{% else %}
<div class="field-wrapper">
  {% if field.field.widget.input_type == 'checkbox' %}
  <label class="checkbox-label" for="{{ field.id_for_label }}">{{ field }} <span>{{ field.label }}</span></label>
  {% else %}
  <label class="form-label" for="{{ field.id_for_label }}">{{ field.label }}{% if field.field.required %}<span class="required-marker" aria-hidden="true"> *</span>{% else %}<span class="optional-label"> (optional)</span>{% endif %}</label>
  {{ field }}
  {% endif %}
  {% if field.help_text %}<div class="field-help" id="{{ field.auto_id }}_helptext">{{ field.help_text }}</div>{% endif %}
  {% if field.errors %}<ul class="field-errors" id="{{ field.auto_id }}_error">{% for error in field.errors %}<li>{{ error }}</li>{% endfor %}</ul>{% endif %}
</div>
{% endif %}
{% endfor %}
```

### `templates/partials/navbar.html`

Transport navigation and an operator link shown only to the correct role.

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
          <li class="nav-item"><a class="nav-link" href="{% url 'emergency:ambulance_start' %}">Ambulance</a></li>
          {% if user.is_staff and perms.emergency.view_ambulancerequest and perms.emergency.change_ambulancerequest %}<li class="nav-item"><a class="nav-link" href="{% url 'emergency:operator_dashboard' %}">Operator queue</a></li>{% endif %}
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

### `templates/partials/footer.html`

Current emergency disclaimer and workflow boundary.

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
        <p class="footer-disclaimer mb-0"><strong>This app does not replace calling 112.</strong> SOS sharing is manual. Transport requests are project records; no ambulance dispatch service is connected.</p>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; {% now 'Y' %} MEDTAP. Built with care.</span>
      <span>Medical Emergency App &middot; Student project</span>
    </div>
  </div>
</footer>
```

### `templates/emergency/detail.html`

Complete SOS sharing page with its new transport link.

```html
{% extends 'base.html' %}
{% block title %}Share your SOS location | MEDTAP{% endblock %}
{% block content %}
<section class="account-section"><div class="container sos-page">
  <div class="sos-heading"><p class="eyebrow">Saved to your account</p><h1>Your request is saved.<br>Now share it.</h1><p>No one has been notified by MEDTAP. Choose how to reach your people below.</p></div>
  <div class="sos-critical-note"><strong>This app does not replace calling 112.</strong> No real ambulance dispatch is confirmed by this app. <a href="tel:112">Call 112 for emergency assistance.</a></div>
  <div class="ambulance-sos-link">{% if ambulance %}<a class="btn btn-outline-primary" href="{% url 'emergency:ambulance_detail' ambulance.pk %}">View project ambulance request</a>{% elif emergency.status == 'active' %}<a class="btn btn-outline-primary" href="{% url 'emergency:ambulance_request' emergency.pk %}">Start project ambulance request</a>{% endif %}<p class="field-help">Saving SOS alone does not create a transport request. The separate project workflow does not contact a dispatch service.</p></div>
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

### `templates/emergency/ambulance_start.html`

The owner's recent saved locations and existing request links.

```html
{% extends 'base.html' %}
{% block title %}Ambulance requests | MEDTAP{% endblock %}
{% block content %}
<section class="account-section"><div class="container sos-page">
  <div class="sos-heading"><p class="eyebrow">Your transport requests</p><h1>One request.<br>A clearer next step.</h1><p>Choose one of your ten most recent saved SOS locations to start or review a project ambulance request.</p></div>
  {% include 'partials/ambulance_notice.html' %}
  <div class="ambulance-location-list">
    {% for location in locations %}<article class="account-panel ambulance-location-card"><div><p class="eyebrow">Saved location</p><h2>{{ location.created_at|date:'d M Y, H:i T' }}</h2><p>{{ location.latitude }}, {{ location.longitude }} · SOS {{ location.get_status_display }}</p></div>
      {% if location.ambulance_request %}<a class="btn btn-primary" href="{% url 'emergency:ambulance_detail' location.ambulance_request.pk %}">View {{ location.ambulance_request.get_status_display|lower }} request</a>{% elif location.status == 'active' %}<a class="btn btn-outline-primary" href="{% url 'emergency:ambulance_request' location.pk %}">Review &amp; request</a>{% else %}<p class="field-help">Only active SOS records can start a new request.</p>{% endif %}
    </article>{% empty %}<div class="account-panel"><h2>Start with a saved location</h2><p>No SOS locations are saved in your account yet.</p></div>{% endfor %}
  </div>
  <a class="btn btn-primary mt-4" href="{% url 'emergency:start' %}">Save a new SOS location {% include 'partials/icon.html' with name='geo-alt' class_name='icon-sm' only %}</a>
</div></section>
{% endblock %}
```

### `templates/emergency/ambulance_request.html`

Review the saved snapshot before a CSRF-protected request POST.

```html
{% extends 'base.html' %}
{% block title %}Review transport request | MEDTAP{% endblock %}
{% block content %}
<section class="account-section"><div class="container account-form-shell">
  <a class="back-link" href="{% url 'emergency:ambulance_start' %}">Back to your requests</a>
  <p class="eyebrow">Check the location first</p><h1>Request transport<br>for this snapshot.</h1>
  {% include 'partials/ambulance_notice.html' %}
  <div class="account-panel"><h2>Your recorded location</h2><p>{{ emergency.latitude }}, {{ emergency.longitude }}</p><p class="text-muted">Saved {{ emergency.created_at|date:'d M Y, H:i T' }}. This snapshot does not follow you as you move.</p>
    <a class="back-link" href="{{ maps_url }}" target="_blank" rel="noopener noreferrer">Check this location in Google Maps</a>
    {% if error %}<div class="form-error-summary" id="form-error-summary" role="alert" tabindex="-1"><h2>Request not created</h2><p>{{ error }}</p></div>{% endif %}
    {% if can_request %}<p>Submitting creates one request in the MEDTAP project queue, visible to authorised operators. Your medical profile and emergency contacts are not included.</p><form method="post">{% csrf_token %}<button type="submit" class="btn btn-primary">Create project ambulance request</button></form>{% else %}<p>Only an active SOS record can start a request. <a href="{% url 'emergency:start' %}">Save a new location</a> if needed.</p>{% endif %}
  </div>
</div></section>
{% endblock %}
```

### `templates/emergency/ambulance_detail.html`

Private progress timeline, manual refresh and polling enhancement.

```html
{% extends 'base.html' %}
{% load static %}
{% block title %}Ambulance request {{ ambulance.pk }} | MEDTAP{% endblock %}
{% block content %}
<section class="account-section"><div class="container sos-page" id="ambulance-progress" data-status-url="{% url 'emergency:ambulance_status' ambulance.pk %}" data-status="{{ ambulance.status }}">
  <a class="back-link" href="{% url 'emergency:ambulance_start' %}">Your transport requests</a>
  <div class="sos-heading"><p class="eyebrow">Project request #{{ ambulance.pk }}</p><h1>Follow each step.<br>Stay informed.</h1><p>Updates below are reported by a project operator. They do not verify a real-world dispatch.</p></div>
  {% include 'partials/ambulance_notice.html' %}
  <div class="sos-layout">
    <section class="account-panel" aria-labelledby="progress-heading"><div class="panel-title-row"><h2 id="progress-heading">Request progress</h2><span class="ambulance-status" id="ambulance-current-status">{{ snapshot.status_label }}</span></div>
      <ol class="ambulance-timeline" aria-label="Operator-reported project progress">{% for step in snapshot.timeline %}<li data-ambulance-step="{{ step.status }}" class="{% if step.is_reached %}ambulance-step-reached{% endif %}{% if step.is_current %} ambulance-step-current{% endif %}"{% if step.is_current %} aria-current="step"{% endif %}><strong>{{ step.label }}</strong><span data-step-time>{% if step.recorded_at %}{{ step.recorded_at|date:'d M Y, H:i T' }}{% elif step.is_reached %}Timestamp not recorded{% else %}Waiting for an operator update{% endif %}</span></li>{% endfor %}</ol>
      <p class="field-help">Times shown in IST. Earlier imported records may have no event timestamps.</p>
      <a class="btn btn-outline-primary" href="{% url 'emergency:ambulance_detail' ambulance.pk %}">Refresh status</a>
      <p class="field-help" id="ambulance-poll-feedback" role="status" aria-live="polite">{% if ambulance.status == 'completed' %}Project workflow completed. Automatic checks are stopped.{% else %}Use Refresh status for the latest update.{% endif %}</p>
      <noscript><p class="field-help">Automatic checks need JavaScript. Refresh status works without it.</p></noscript>
    </section>
    <section class="account-panel" aria-labelledby="trip-location-heading"><p class="eyebrow">Your saved snapshot</p><h2 id="trip-location-heading">Location &amp; reference</h2><p>{{ ambulance.emergency.latitude }}, {{ ambulance.emergency.longitude }}</p><p class="field-help">Location saved {{ ambulance.emergency.created_at|date:'d M Y, H:i T' }}. It does not update as you move.</p><a class="back-link" href="{{ maps_url }}" target="_blank" rel="noopener noreferrer">View recorded location in Google Maps</a>
      <h3 class="ambulance-reference-heading">Reference facility</h3><p id="ambulance-facility-name">{% if snapshot.facility %}{{ snapshot.facility.name }}{% else %}No reference facility selected{% endif %}</p><p id="ambulance-facility-demo" class="facility-demo-label"{% if not snapshot.facility.is_demo %} hidden{% endif %}>FAKE sample — not a real provider</p><p class="field-help">A directory reference does not confirm an ambulance, beds or provider participation.</p>
      <a class="back-link" href="{% url 'emergency:detail' ambulance.emergency_id %}">Open your SOS sharing message</a>
    </section>
  </div>
</div></section>
{% endblock %}
{% block extra_js %}<script src="{% static 'js/ambulance.js' %}" defer></script>{% endblock %}
```

### `templates/emergency/operator_dashboard.html`

Status counts, filtering and a paginated operator queue.

```html
{% extends 'base.html' %}
{% block title %}Operator queue | MEDTAP{% endblock %}
{% block content %}
<section class="account-section"><div class="container sos-page">
  <div class="sos-heading"><p class="eyebrow">Authorised operators only</p><h1>The transport queue.</h1><p>Review project requests and record the next workflow step.</p></div>
  {% include 'partials/ambulance_notice.html' %}
  <div class="operator-counts"><div><strong>{{ counts.requested }}</strong><span>Requested</span></div><div><strong>{{ counts.progressing }}</strong><span>In progress</span></div><div><strong>{{ counts.completed }}</strong><span>Completed</span></div></div>
  <form method="get" class="operator-filter"><div class="field-wrapper"><label class="form-label" for="{{ form.status.id_for_label }}">Show</label>{{ form.status }}</div><button class="btn btn-primary" type="submit">Filter queue</button></form>
  {% include 'partials/form_errors.html' with form=form error_heading='Please check the queue filter' only %}
  <div class="ambulance-location-list">{% for ambulance in page_obj %}<article class="account-panel operator-queue-card"><div><p class="eyebrow">Project request #{{ ambulance.pk }}</p><h2>{% if ambulance.emergency.user %}{{ ambulance.emergency.user.username }}{% else %}Deleted account{% endif %}</h2><p class="field-help">Requested {{ ambulance.created_at|date:'d M Y, H:i T' }}</p></div><span class="ambulance-status">{{ ambulance.get_status_display }}</span><a class="btn btn-outline-primary" href="{% url 'emergency:operator_update' ambulance.pk %}">Review &amp; update</a></article>{% empty %}<div class="account-panel"><h2>No requests in this view</h2><p class="text-muted">Choose another status or refresh the queue later.</p></div>{% endfor %}</div>
  {% if page_obj.paginator.num_pages > 1 %}<nav class="finder-pagination" aria-label="Operator queue pages">{% if previous_query %}<a class="btn btn-outline-primary" href="{{ previous_query }}">Previous</a>{% endif %}<span>Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>{% if next_query %}<a class="btn btn-outline-primary" href="{{ next_query }}">Next</a>{% endif %}</nav>{% endif %}
</div></section>
{% endblock %}
```

### `templates/emergency/operator_update.html`

Validated operator form, snapshot location and recorded event history.

```html
{% extends 'base.html' %}
{% block title %}Update project request {{ ambulance.pk }} | MEDTAP{% endblock %}
{% block content %}
<section class="account-section"><div class="container sos-page">
  <a class="back-link" href="{% url 'emergency:operator_dashboard' %}">Back to the operator queue</a><div class="sos-heading"><p class="eyebrow">Project request #{{ ambulance.pk }}</p><h1>Record the next step.</h1></div>
  {% include 'partials/ambulance_notice.html' %}
  <div class="sos-layout"><section class="account-panel" aria-labelledby="update-heading"><h2 id="update-heading">Operator update</h2><p class="text-muted">Keep the current status or advance by one step. Every status change records who changed it and when.</p>
    {% include 'partials/form_errors.html' with form=form error_heading='Update not saved' only %}
    <form method="post">{% csrf_token %}{% include 'partials/form_fields.html' with form=form only %}<button class="btn btn-primary" type="submit">Save project update</button></form>
    <a class="back-link mt-3" href="{% url 'emergency:operator_update' ambulance.pk %}">Reload latest request</a><p class="field-help">FAKE sample facilities remain fictional. No provider is contacted when you select a reference.</p>
  </section><section class="account-panel" aria-labelledby="operator-location-heading"><h2 id="operator-location-heading">Recorded location</h2><p>{{ ambulance.emergency.latitude }}, {{ ambulance.emergency.longitude }}</p><p class="field-help">Snapshot saved {{ ambulance.emergency.created_at|date:'d M Y, H:i T' }}. Confirm the location through your real-world procedure before acting.</p><a class="back-link" href="{{ maps_url }}" target="_blank" rel="noopener noreferrer">Open recorded location in Google Maps</a>
    <h3 class="ambulance-reference-heading">Recorded status history</h3><ul class="operator-event-list">{% for event in ambulance.status_events.all %}<li><strong>{{ event.get_status_display }}</strong><span>{{ event.created_at|date:'d M Y, H:i T' }} · {% if event.changed_by %}{{ event.changed_by.username }}{% else %}Deleted account{% endif %}</span></li>{% empty %}<li>No earlier event history was recorded for this request.</li>{% endfor %}</ul>
  </section></div>
</div></section>
{% endblock %}
```

### `static/css/theme.css`

Complete current theme, including all previous screens and responsive ambulance styles.

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
/* Ambulance project requests and operator queue. */
.ambulance-location-list { display: grid; gap: 1rem; }
.ambulance-location-card, .operator-queue-card { display: flex; flex-wrap: wrap; gap: 1.2rem; align-items: center; justify-content: space-between; }
.ambulance-location-card h2 { font-size: 1.35rem; }
.ambulance-location-card p:last-child { color: var(--muted); margin-bottom: 0; }
.ambulance-status { display: inline-flex; align-items: center; min-height: 36px; border-radius: 999px; background: var(--blue-soft); color: var(--primary-dark); padding: .35rem .8rem; font-weight: 600; font-size: .85rem; }
.ambulance-timeline { list-style: none; padding: 0; margin: 1.8rem 0; }
.ambulance-timeline li { position: relative; margin-left: .5rem; padding: 0 0 1.6rem 1.7rem; border-left: 2px solid var(--border); }
.ambulance-timeline li:last-child { padding-bottom: .3rem; border-left-color: transparent; }
.ambulance-timeline li::before { content: ''; position: absolute; left: -7px; top: .3rem; width: 12px; height: 12px; border-radius: 50%; border: 2px solid var(--muted); background: white; }
.ambulance-timeline .ambulance-step-reached::before { border-color: var(--accent-dark); background: var(--accent-dark); }
.ambulance-timeline .ambulance-step-current::before { outline: 3px solid #B8DCD3; outline-offset: 2px; }
.ambulance-timeline strong { display: block; color: var(--ink); font-weight: 500; }
.ambulance-timeline span { display: block; margin-top: .25rem; color: var(--muted); font-size: .85rem; }
.ambulance-reference-heading { font-size: 1.1rem; margin-top: 1.6rem; }
.ambulance-sos-link { margin: 0 0 1.5rem; }
.operator-counts { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.5rem 0; }
.operator-counts > div { background: var(--hero-bg); border: 1px solid var(--border); border-radius: 1rem; padding: 1.2rem; }
.operator-counts strong, .operator-counts span { display: block; }
.operator-counts strong { color: var(--ink); font-size: 2rem; font-weight: 500; }
.operator-counts span { color: var(--muted); font-size: .9rem; }
.operator-filter { display: flex; align-items: end; flex-wrap: wrap; gap: 1rem; margin: 1.4rem 0; }
.operator-filter .field-wrapper { margin: 0; min-width: 200px; }
.operator-queue-card h2 { font-size: 1.25rem; overflow-wrap: anywhere; }
.operator-queue-card .eyebrow { margin-bottom: .4rem; }
.operator-event-list { list-style: none; padding: 0; margin: 1rem 0; }
.operator-event-list li { border-top: 1px solid var(--border); padding: .9rem 0; }
.operator-event-list strong, .operator-event-list span { display: block; }
.operator-event-list strong { font-weight: 500; }
.operator-event-list span { color: var(--muted); font-size: .85rem; overflow-wrap: anywhere; }
@media (min-width: 992px) and (max-width: 1199.98px) {
  .navbar .nav-link { padding-inline: .45rem !important; font-size: .8rem; }
  .navbar-actions .btn { padding-inline: .7rem; font-size: .8rem; }
  .navbar-brand { margin-right: .7rem; }
}
@media (max-width: 575.98px) {
  .operator-counts { gap: .5rem; }
  .operator-counts > div { padding: .8rem; }
  .operator-counts span { font-size: .8rem; }
  .operator-queue-card { gap: .8rem; }
  .operator-queue-card > div:first-child { width: 100%; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

### `static/js/ambulance.js`

Read-only periodic status updates with visible failure/manual-refresh handling.

```javascript
"use strict";

(() => {
  const root = document.getElementById("ambulance-progress");
  if (!root) return;
  const feedback = document.getElementById("ambulance-poll-feedback");
  const steps = [...root.querySelectorAll("[data-ambulance-step]")];
  let stopped = root.dataset.status === "completed";
  let busy = false;
  let timer;
  const dateFormat = new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Kolkata",
  });

  function schedule() {
    if (!stopped && document.visibilityState !== "hidden") timer = setTimeout(refresh, 10000);
  }

  async function refresh() {
    if (stopped || busy || document.visibilityState === "hidden") return;
    busy = true;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(root.dataset.statusUrl, {
        credentials: "same-origin", cache: "no-store", headers: { Accept: "application/json" },
        signal: controller.signal,
      });
      if (!response.ok || response.redirected) throw new Error("Status unavailable");
      const data = await response.json();
      if (!steps.some((step) => step.dataset.ambulanceStep === data.status) || !Array.isArray(data.timeline)) {
        throw new Error("Invalid progress response");
      }
      document.getElementById("ambulance-current-status").textContent = data.status_label;
      for (const element of steps) {
        const step = data.timeline.find((item) => item.status === element.dataset.ambulanceStep);
        if (!step) throw new Error("Missing progress step");
        element.classList.toggle("ambulance-step-reached", step.is_reached);
        element.classList.toggle("ambulance-step-current", step.is_current);
        if (step.is_current) element.setAttribute("aria-current", "step");
        else element.removeAttribute("aria-current");
        element.querySelector("[data-step-time]").textContent = step.recorded_at
          ? dateFormat.format(new Date(step.recorded_at)) + " IST"
          : step.is_reached ? "Timestamp not recorded" : "Waiting for an operator update";
      }
      document.getElementById("ambulance-facility-name").textContent = data.facility
        ? data.facility.name : "No reference facility selected";
      document.getElementById("ambulance-facility-demo").hidden = !data.facility?.is_demo;
      root.dataset.status = data.status;
      stopped = data.status === "completed";
      feedback.textContent = stopped
        ? "Project workflow completed. Automatic checks are stopped."
        : "Latest operator-reported project status loaded. Checks every 10 seconds while this page is visible.";
    } catch {
      stopped = true;
      feedback.textContent = "Automatic updates are paused. Use Refresh status to reconnect or sign in again. The last displayed status may be out of date.";
    } finally {
      clearTimeout(timeout);
      busy = false;
      schedule();
    }
  }

  document.addEventListener("visibilitychange", () => {
    clearTimeout(timer);
    if (!stopped && document.visibilityState !== "hidden") refresh();
  });
  if (!stopped) feedback.textContent = "Checking operator-reported project status every 10 seconds while this page is visible.";
  schedule();
})();
```

### `emergency/test_ambulance.py`

Thirty-one new Django tests using fictional users and isolated databases.

```python
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command
from django.http import Http404
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User
from facilities.models import Facility

from .ambulance_services import ambulance_snapshot, request_ambulance, update_ambulance
from .forms import AmbulanceOperatorForm
from .models import AmbulanceRequest, AmbulanceStatusEvent, EmergencyRequest
from .permissions import can_operate


class AmbulanceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username="ambulance-fake-owner")
        cls.other = User.objects.create_user(username="ambulance-fake-other")
        cls.operator = User.objects.create_user(username="ambulance-fake-operator", is_staff=True)
        cls.operator.user_permissions.add(*Permission.objects.filter(
            content_type__app_label="emergency", codename__in=["view_ambulancerequest", "change_ambulancerequest"],
        ))
        cls.sos = EmergencyRequest.objects.create(user=cls.owner, latitude=0, longitude=0)
        cls.facility = Facility.objects.create(
            name="FAKE Ambulance Test Hospital", facility_type="hospital", address="FAKE test address",
            phone="0000000000", latitude=0, longitude=0, demo_key="ambulance-test-demo",
        )

    def new_request(self):
        return request_ambulance(user=self.owner, emergency_pk=self.sos.pk)[0]

    def update(self, ambulance, **changes):
        values = dict(operator=self.operator, pk=ambulance.pk, expected_version=ambulance.version,
                      status=ambulance.status, facility=None, operator_notes="")
        values.update(changes)
        return update_ambulance(**values)


class AmbulanceServiceTests(AmbulanceTestCase):
    def test_request_and_retry_have_one_record_and_one_initial_event(self):
        first, created = request_ambulance(user=self.owner, emergency_pk=self.sos.pk)
        second, repeated = request_ambulance(user=self.owner, emergency_pk=self.sos.pk)
        self.assertTrue(created)
        self.assertFalse(repeated)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(AmbulanceStatusEvent.objects.count(), 1)
        self.assertEqual(first.status_events.get().changed_by_id, self.owner.pk)

    def test_other_users_cannot_request_for_a_known_sos_uuid(self):
        with self.assertRaises(Http404):
            request_ambulance(user=self.other, emergency_pk=self.sos.pk)

    def test_inactive_sos_cannot_start_new_request(self):
        for state in ("resolved", "cancelled"):
            self.sos.status = state
            self.sos.save()
            with self.assertRaises(ValidationError):
                self.new_request()
        self.assertEqual(AmbulanceRequest.objects.count(), 0)

    def test_full_forward_flow_records_actual_status_actors_and_versions(self):
        ambulance = self.new_request()
        for target in ("accepted", "on_the_way", "completed"):
            ambulance = self.update(ambulance, status=target)
        self.assertEqual(ambulance.version, 3)
        events = list(ambulance.status_events.all())
        self.assertEqual([e.status for e in events], ["requested", "accepted", "on_the_way", "completed"])
        self.assertTrue(all(e.changed_by_id == self.operator.pk for e in events[1:]))
        self.assertTrue(all(e.created_at for e in events))
        self.sos.refresh_from_db()
        self.assertEqual(self.sos.status, "active")

    def test_skip_reverse_and_reopen_are_rejected(self):
        ambulance = self.new_request()
        with self.assertRaises(ValidationError):
            self.update(ambulance, status="completed")
        ambulance = self.update(ambulance, status="accepted")
        with self.assertRaises(ValidationError):
            self.update(ambulance, status="requested")
        ambulance = self.update(ambulance, status="on_the_way")
        ambulance = self.update(ambulance, status="completed")
        with self.assertRaises(ValidationError):
            self.update(ambulance, status="requested")

    def test_same_status_note_edit_increments_version_without_fake_transition_event(self):
        ambulance = self.update(self.new_request(), operator_notes="Internal test note")
        self.assertEqual(ambulance.version, 1)
        self.assertEqual(ambulance.status_events.count(), 1)
        self.assertEqual(ambulance.operator_notes, "Internal test note")

    def test_stale_version_preserves_newer_notes_and_status(self):
        old = self.new_request()
        self.update(old, status="accepted", operator_notes="Newer note")
        with self.assertRaises(ValidationError) as error:
            self.update(old, operator_notes="Stale note")
        self.assertEqual(error.exception.code, "stale")
        old.refresh_from_db()
        self.assertEqual(old.operator_notes, "Newer note")
        self.assertEqual(old.status, "accepted")
        self.assertEqual(old.status_events.count(), 2)

    def test_conditional_write_race_returns_stale_without_recording_an_event(self):
        ambulance = self.new_request()
        with patch("django.db.models.query.QuerySet.update", return_value=0):
            with self.assertRaises(ValidationError) as error:
                self.update(ambulance, status="accepted")
        self.assertEqual(error.exception.code, "stale")
        self.assertEqual(ambulance.status_events.count(), 1)

    def test_event_failure_rolls_back_status_and_version_together(self):
        ambulance = self.new_request()
        with patch.object(AmbulanceStatusEvent.objects, "create", side_effect=ValidationError("event failed")):
            with self.assertRaises(ValidationError):
                self.update(ambulance, status="accepted")
        ambulance.refresh_from_db()
        self.assertEqual(ambulance.status, "requested")
        self.assertEqual(ambulance.version, 0)

    def test_initial_event_failure_rolls_back_request_creation(self):
        with patch.object(AmbulanceStatusEvent.objects, "create", side_effect=ValidationError("event failed")):
            with self.assertRaises(ValidationError):
                self.new_request()
        self.assertEqual(AmbulanceRequest.objects.count(), 0)

    def test_only_active_hospital_clinic_can_be_new_reference(self):
        ambulance = self.new_request()
        ambulance = self.update(ambulance, facility=self.facility)
        self.assertEqual(ambulance.facility_id, self.facility.pk)
        self.assertTrue(ambulance_snapshot(ambulance)["facility"]["is_demo"])
        self.facility.is_active = False
        self.facility.save()
        # An existing reference can be retained after it becomes inactive.
        ambulance = self.update(ambulance, facility=self.facility, status="accepted")
        ambulance = self.update(ambulance, facility=None)
        with self.assertRaises(ValidationError):
            self.update(ambulance, facility=self.facility)
        self.facility.is_active = True
        self.facility.facility_type = "pharmacy"
        self.facility.save()
        with self.assertRaises(ValidationError):
            self.update(ambulance, facility=self.facility)

    def test_regular_user_cannot_call_operator_service_directly(self):
        with self.assertRaises(PermissionDenied):
            self.update(self.new_request(), operator=self.owner, status="accepted")

    def test_existing_request_retry_is_still_same_record_after_completion(self):
        ambulance = self.new_request()
        for target in ("accepted", "on_the_way", "completed"):
            ambulance = self.update(ambulance, status=target)
        self.sos.status = "resolved"
        self.sos.save()
        repeat, created = request_ambulance(user=self.owner, emergency_pk=self.sos.pk)
        self.assertFalse(created)
        self.assertEqual(repeat.pk, ambulance.pk)

    def test_snapshot_never_exposes_internal_notes_or_operator_identity(self):
        ambulance = self.update(self.new_request(), status="accepted", operator_notes="PRIVATE OPERATOR NOTE")
        data = ambulance_snapshot(ambulance)
        self.assertNotIn("operator_notes", data)
        self.assertNotIn("changed_by", str(data))
        self.assertNotIn("PRIVATE OPERATOR NOTE", str(data))
        self.assertIsNotNone(data["timeline"][1]["recorded_at"])
        self.assertIsNone(data["timeline"][2]["recorded_at"])

    def test_legacy_record_has_no_invented_event_timestamps(self):
        legacy = AmbulanceRequest.objects.create(emergency=self.sos, status="accepted")
        self.assertTrue(all(step["recorded_at"] is None for step in ambulance_snapshot(legacy)["timeline"]))

    def test_deleting_reference_or_operator_keeps_request_history(self):
        ambulance = self.update(self.new_request(), status="accepted", facility=self.facility)
        self.facility.delete()
        self.operator.delete()
        ambulance.refresh_from_db()
        self.assertIsNone(ambulance.facility_id)
        self.assertIsNone(ambulance.status_events.get(status="accepted").changed_by_id)


class AmbulanceViewsTests(AmbulanceTestCase):
    def setUp(self):
        self.client.force_login(self.owner)

    def operator_payload(self, ambulance, **changes):
        values = {"expected_version": ambulance.version, "status": "accepted", "facility": "", "operator_notes": ""}
        values.update(changes)
        return values

    def test_guest_login_and_review_get_never_create_requests(self):
        url = reverse("emergency:ambulance_request", args=[self.sos.pk])
        self.assertContains(self.client.get(url), "Create project ambulance request")
        self.assertEqual(AmbulanceRequest.objects.count(), 0)
        self.client.logout()
        self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertEqual(AmbulanceRequest.objects.count(), 0)

    def test_creation_redirects_and_duplicate_submit_reuses_record(self):
        url = reverse("emergency:ambulance_request", args=[self.sos.pk])
        first = self.client.post(url)
        second = self.client.post(url)
        self.assertEqual(first.status_code, 302)
        self.assertEqual(first.url, second.url)
        self.assertEqual(AmbulanceRequest.objects.count(), 1)
        self.assertEqual(AmbulanceStatusEvent.objects.count(), 1)

    def test_forbidden_user_cannot_read_or_write_other_users_records(self):
        ambulance = self.new_request()
        self.client.force_login(self.other)
        for name, pk in (("ambulance_request", self.sos.pk), ("ambulance_detail", ambulance.pk), ("ambulance_status", ambulance.pk)):
            self.assertEqual(self.client.get(reverse(f"emergency:{name}", args=[pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("emergency:ambulance_request", args=[self.sos.pk])).status_code, 404)

    def test_owner_detail_and_poll_are_read_only_and_exclude_internal_notes(self):
        ambulance = self.update(self.new_request(), operator_notes="TOP SECRET NOTE")
        detail = reverse("emergency:ambulance_detail", args=[ambulance.pk])
        api = reverse("emergency:ambulance_status", args=[ambulance.pk])
        html = self.client.get(detail)
        self.assertContains(html, "Project workflow")
        self.assertNotContains(html, "TOP SECRET NOTE")
        data = self.client.get(api)
        self.assertEqual(data.json()["status"], "requested")
        self.assertNotContains(data, "TOP SECRET NOTE")
        for url in (detail, api):
            self.assertIn("no-store", self.client.get(url)["Cache-Control"])
            self.assertEqual(self.client.post(url).status_code, 405)

    def test_owner_cannot_use_operator_endpoints(self):
        ambulance = self.new_request()
        for url in (reverse("emergency:operator_dashboard"), reverse("emergency:operator_update", args=[ambulance.pk])):
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url).status_code, 403)

    def test_staff_flag_and_both_permissions_are_required(self):
        ambulance = self.new_request()
        url = reverse("emergency:operator_update", args=[ambulance.pk])
        for staff, permissions in ((True, []), (False, ["view_ambulancerequest", "change_ambulancerequest"]), (True, ["view_ambulancerequest"])):
            user = User.objects.create_user(username=f"fake-access-{staff}-{len(permissions)}", is_staff=staff)
            user.user_permissions.set(Permission.objects.filter(content_type__app_label="emergency", codename__in=permissions))
            self.client.force_login(user)
            self.assertEqual(self.client.get(url).status_code, 403)
        self.client.force_login(self.operator)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_authorised_operator_posts_next_status_and_internal_notes(self):
        ambulance = self.new_request()
        self.client.force_login(self.operator)
        url = reverse("emergency:operator_update", args=[ambulance.pk])
        response = self.client.post(url, self.operator_payload(ambulance, operator_notes="Operator only"))
        self.assertRedirects(response, url)
        ambulance.refresh_from_db()
        self.assertEqual(ambulance.status, "accepted")
        self.assertEqual(ambulance.operator_notes, "Operator only")
        self.assertEqual(ambulance.status_events.count(), 2)

    def test_invalid_status_notes_and_missing_version_return_errors(self):
        ambulance = self.new_request()
        self.client.force_login(self.operator)
        url = reverse("emergency:operator_update", args=[ambulance.pk])
        for changes in ({"status": "completed"}, {"expected_version": ""}, {"operator_notes": "x" * 2001}):
            response = self.client.post(url, self.operator_payload(ambulance, **changes))
            self.assertContains(response, "Update not saved", status_code=400)
        ambulance.refresh_from_db()
        self.assertEqual(ambulance.status, "requested")

    def test_stale_html_form_returns_409_including_when_old_status_is_no_longer_allowed(self):
        ambulance = self.new_request()
        old_data = self.operator_payload(ambulance, status="requested")
        self.update(ambulance, status="accepted")
        self.client.force_login(self.operator)
        response = self.client.post(reverse("emergency:operator_update", args=[ambulance.pk]), old_data)
        self.assertContains(response, "Reload the latest version", status_code=409)

    def test_operator_form_only_offers_current_next_and_valid_reference_choices(self):
        ambulance = self.new_request()
        form = AmbulanceOperatorForm(ambulance=ambulance)
        self.assertEqual([value for value, _ in form.fields["status"].choices], ["requested", "accepted"])
        self.assertIn(self.facility, form.fields["facility"].queryset)
        self.assertIn("FAKE sample", form.fields["facility"].label_from_instance(self.facility))
        self.facility.is_active = False
        self.facility.save()
        self.assertNotIn(self.facility, AmbulanceOperatorForm(ambulance=ambulance).fields["facility"].queryset)

    def test_csrf_protects_owner_creation_and_operator_updates(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        url = reverse("emergency:ambulance_request", args=[self.sos.pk])
        self.assertEqual(client.post(url).status_code, 403)
        client.get(url)
        self.assertEqual(client.post(url, {"csrfmiddlewaretoken": client.cookies["csrftoken"].value}).status_code, 302)
        ambulance = AmbulanceRequest.objects.get()
        client.force_login(self.operator)
        url = reverse("emergency:operator_update", args=[ambulance.pk])
        self.assertEqual(client.post(url, self.operator_payload(ambulance)).status_code, 403)
        client.get(url)
        self.assertEqual(client.post(url, self.operator_payload(ambulance, csrfmiddlewaretoken=client.cookies["csrftoken"].value)).status_code, 302)

    def test_dashboard_filter_counts_and_pagination(self):
        for index in range(27):
            sos = EmergencyRequest.objects.create(user=self.owner, latitude=0, longitude=0)
            AmbulanceRequest.objects.create(emergency=sos, status="completed" if index == 0 else "requested")
        self.client.force_login(self.operator)
        url = reverse("emergency:operator_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.context["counts"], {"requested": 26, "progressing": 0, "completed": 1})
        self.assertEqual(response.context["page_obj"].paginator.count, 26)
        self.assertEqual(len(response.context["page_obj"].object_list), 25)
        self.assertEqual(self.client.get(url, {"status": "completed"}).context["page_obj"].paginator.count, 1)
        self.assertIn("status=all", self.client.get(url, {"status": "all"}).context["next_query"])
        self.assertEqual(self.client.get(url, {"status": "bad"}).status_code, 400)
        self.assertEqual(self.client.get(url, {"page": 99}).status_code, 404)

    def test_ordinary_navigation_does_not_show_operator_link(self):
        response = self.client.get(reverse("core:home"))
        self.assertNotContains(response, 'href="/emergency/operators/ambulances/"')
        self.client.force_login(self.operator)
        self.assertContains(self.client.get(reverse("core:home")), 'href="/emergency/operators/ambulances/"')

    def test_home_and_sos_offer_working_request_links(self):
        self.assertContains(self.client.get(reverse("core:home")), 'href="/emergency/ambulance/"')
        self.assertContains(self.client.get(reverse("emergency:detail", args=[self.sos.pk])), 'Start project ambulance request')
        ambulance = self.new_request()
        self.assertContains(self.client.get(reverse("emergency:detail", args=[self.sos.pk])), 'View project ambulance request')
        self.assertContains(self.client.get(reverse("emergency:ambulance_start")), reverse("emergency:ambulance_detail", args=[ambulance.pk]))


class OperatorGroupTests(TestCase):
    def test_setup_is_repeatable_and_does_not_assign_or_promote_users(self):
        user = User.objects.create_user(username="fake-group-user")
        output = StringIO()
        call_command("setup_ambulance_operators", stdout=output)
        call_command("setup_ambulance_operators", stdout=output)
        group = Group.objects.get(name="Ambulance operators")
        self.assertEqual(group.permissions.count(), 2)
        self.assertEqual(group.user_set.count(), 0)
        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertFalse(can_operate(user))
```

### `emergency/ambulance_frontend_tests.cjs`

Eight browser-API mock checks with no real network or transport activity.

```javascript
// Browser API mocks only: no real transport, GPS or network request.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const code = fs.readFileSync(path.join(__dirname, "..", "static", "js", "ambulance.js"), "utf8");
const statuses = ["requested", "accepted", "on_the_way", "completed"];
const settle = () => new Promise(setImmediate);

function node() {
  const element = { textContent: "", hidden: false, attributes: {}, classes: new Map(),
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
  };
  element.classList = { toggle: (name, value) => element.classes.set(name, value) };
  Object.defineProperty(element, "innerHTML", { set() { throw Error("Unsafe HTML insertion"); } });
  return element;
}
function snapshot(status = "accepted") {
  const current = statuses.indexOf(status);
  return { status, status_label: status === "accepted" ? "Accepted" : "Completed", facility: null,
    timeline: statuses.map((value, index) => ({ status: value, is_reached: index <= current,
      is_current: index === current, recorded_at: index <= current ? "2026-11-12T12:00:00Z" : null })) };
}
function fixture({ initial = "requested", hidden = false, response } = {}) {
  const elements = {};
  for (const id of ["ambulance-poll-feedback", "ambulance-current-status", "ambulance-facility-name", "ambulance-facility-demo"]) elements[id] = node();
  elements["ambulance-current-status"].textContent = "Requested";
  const steps = statuses.map((status) => {
    const element = node(); element.dataset = { ambulanceStep: status };
    element.time = node(); element.querySelector = () => element.time;
    return element;
  });
  const root = { dataset: { status: initial, statusUrl: "/emergency/ambulance/1/status/" }, querySelectorAll: () => steps };
  const timers = new Map(), events = {}, calls = [];
  let timerId = 0;
  const document = { visibilityState: hidden ? "hidden" : "visible",
    getElementById: (id) => id === "ambulance-progress" ? root : elements[id],
    addEventListener: (name, callback) => { events[name] = callback; },
  };
  vm.runInNewContext(code, {
    document, Intl, Date, AbortController,
    setTimeout: (callback, delay) => { timerId += 1; timers.set(timerId, { callback, delay }); return timerId; },
    clearTimeout: (id) => timers.delete(id),
    fetch: async (url, options) => {
      calls.push({ url, options });
      if (response instanceof Error) throw response;
      return response || { ok: true, redirected: false, json: async () => snapshot() };
    },
  });
  return { elements, steps, root, timers, document, calls,
    async tick() {
      const [id, timer] = [...timers][0]; timers.delete(id); await timer.callback();
    },
    async show() { document.visibilityState = "visible"; events.visibilitychange(); await settle(); },
  };
}

(async () => {
  let count = 0;
  async function test(name, run) { await run(); count += 1; console.log(`PASS ${name}`); }
  await test("polling waits ten seconds and only performs an authenticated read", async () => {
    const state = fixture();
    assert.equal(state.calls.length, 0);
    assert.equal([...state.timers.values()][0].delay, 10000);
    await state.tick();
    assert.equal(state.calls.length, 1);
    assert.equal(state.calls[0].options.credentials, "same-origin");
    assert.equal(state.calls[0].options.cache, "no-store");
    assert.equal(state.calls[0].options.method, undefined);
  });
  await test("an update changes status and recorded timeline accessibly", async () => {
    const state = fixture(); await state.tick();
    assert.equal(state.elements["ambulance-current-status"].textContent, "Accepted");
    assert.equal(state.steps[1].attributes["aria-current"], "step");
    assert.equal(state.steps[2].time.textContent, "Waiting for an operator update");
    assert.match(state.steps[1].time.textContent, /IST/);
  });
  await test("hidden tabs do not poll and resume when visible", async () => {
    const state = fixture({ hidden: true });
    assert.equal(state.timers.size, 0);
    assert.equal(state.calls.length, 0);
    await state.show();
    assert.equal(state.calls.length, 1);
  });
  await test("completed initial requests never poll", () => {
    const state = fixture({ initial: "completed" });
    assert.equal(state.timers.size, 0);
    assert.equal(state.calls.length, 0);
  });
  await test("a received completion stops subsequent checks", async () => {
    const state = fixture({ response: { ok: true, json: async () => snapshot("completed") } });
    await state.tick();
    assert.equal(state.timers.size, 0);
    assert.match(state.elements["ambulance-poll-feedback"].textContent, /checks are stopped/);
  });
  await test("network failures and expired sessions preserve the last status with a refresh fallback", async () => {
    for (const response of [new Error("offline"), { ok: false }, { ok: true, redirected: true }]) {
      const state = fixture({ response }); await state.tick();
      assert.equal(state.elements["ambulance-current-status"].textContent, "Requested");
      assert.match(state.elements["ambulance-poll-feedback"].textContent, /out of date/);
      assert.equal(state.timers.size, 0);
    }
  });
  await test("facility names are inserted as text and demo flags stay visible", async () => {
    const data = snapshot(); data.facility = { name: "<img onerror=alert(1)>", is_demo: true };
    const state = fixture({ response: { ok: true, json: async () => data } });
    await state.tick();
    assert.equal(state.elements["ambulance-facility-name"].textContent, data.facility.name);
    assert.equal(state.elements["ambulance-facility-demo"].hidden, false);
  });
  await test("invalid status payload pauses rather than implying progress", async () => {
    const state = fixture({ response: { ok: true, json: async () => ({ status: "dispatched", timeline: [] }) } });
    await state.tick();
    assert.equal(state.elements["ambulance-current-status"].textContent, "Requested");
    assert.equal(state.timers.size, 0);
  });
  console.log(`${count} ambulance frontend checks passed.`);
})().catch((error) => { console.error(error); process.exitCode = 1; });
```

Stop here. Say **"next"** for first-aid guides and verified emergency helpline pages.
