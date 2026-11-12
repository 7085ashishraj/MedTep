# Step 9 — Main model/view tests and project verification

This step is implemented in your workspace. Complete Steps 1–8 first. It adds
focused regression tests and one repeatable check command. It does not change
the UI, application views, data models, `.env`, dependencies or migration files.
Full copy-paste source for the three new files appears below.

## What this step adds

Earlier features already include 178 Django tests and 38 isolated JavaScript
checks. This step adds **14 Django tests**, bringing the total to **192**.
Rather than repeating existing field-validation tests, it verifies workflows
across app boundaries and invariants enforced by the migrated database itself.

| New coverage | What a regression would look like |
| --- | --- |
| Register → medical profile → contact → SOS → transport → operator updates → logout → login | Individual views pass, but a session, CSRF token, redirect or version fails when the features are used together. |
| CSRF token rotation during registration/sign-in | A token from the pre-login form can still change medical details after authentication. |
| SOS after logout | An expired signed-in page can create a record, or the app redirects back to a POST-only endpoint. |
| Operator permission revoked during an active session | The existing session retains update access after its change permission is removed. |
| Public APIs in a signed-in session | Directory or educational JSON accidentally includes profile, contact, SOS or internal operator data. |
| Direct database writes | Duplicate profiles, duplicate primary contacts, invalid coordinates, duplicate transport/events or invalid step positions are stored when form validation is bypassed. |
| Deleting a fictional account | Related contacts/profile remain unexpectedly, or emergency history is deleted despite its SET_NULL design. |

## Folder structure for this step

```text
MEDTAP/
├── scripts/
│   └── check_project.py         # one command for all seven check groups
├── core/
│   ├── test_workflows.py        # 5 cross-app HTTP tests; CSRF checks enabled
│   ├── test_database.py         # 9 direct-write database-invariant tests
│   ├── test_ui.py               # existing 9 UI/error-handler tests
│   └── ui_frontend_tests.cjs    # existing 9 shared JS checks
├── accounts/tests.py
├── facilities/
│   ├── tests.py
│   ├── test_nearby.py
│   └── frontend_tests.cjs
├── emergency/
│   ├── tests.py
│   ├── test_ambulance.py
│   ├── frontend_tests.cjs
│   └── ambulance_frontend_tests.cjs
├── firstaid/tests.py
├── README.md                    # current progress and test commands
└── STEP_9.md
```

Keep the earlier tests: these new modules supplement them. `core` is already an
installed app, so Django discovers the new `test_*.py` files without configuration
changes. `scripts/check_project.py` is an ordinary script, not a Django app.

## Exact terminal commands

### Recommended: one command in PowerShell

From the MEDTAP directory in VS Code:

```powershell
.\.venv\Scripts\python.exe scripts/check_project.py
```

The runner uses that same Python interpreter for every Django command and an
absolute project working directory. It works even if called from another folder.
On macOS/Linux, the equivalent command is:

```bash
./.venv/bin/python scripts/check_project.py
```

Python dependencies are already installed in your existing virtual environment.
Node.js must be available on PATH for the four existing JavaScript checks. It is
not required for running the Django website. If Node is absent, the runner tells
you what is missing and exits unsuccessfully instead of silently skipping checks.

The runner performs these seven groups, in order:

1. Django system checks.
2. Migration drift detection with `makemigrations --check --dry-run`.
3. All 192 Django tests with `--noinput`.
4. The 9 shared UI JavaScript checks.
5. The 9 facility JavaScript checks.
6. The 12 SOS JavaScript checks.
7. The 8 ambulance JavaScript checks.

Expected final output includes:

```text
System check identified no issues (0 silenced).
No changes detected
Found 192 test(s).
...
Ran 192 tests in ...s
OK
...
9 shared UI checks passed.
9 frontend checks passed.
12 SOS frontend checks passed.
8 ambulance frontend checks passed.

All 7 project check groups passed.
```

The exact order of Django's progress/status lines and elapsed time can vary.
The process exits with status 0 on success. A failed command stops the runner,
prints the failed group and returns a nonzero status. Fix that error before
rerunning; a success message is never printed after a failed group.

Only child processes receive a newly generated temporary Django signing key,
`DEBUG=False` and local/test hosts. The runner does not change your `.env` or
the settings of an already running server. The key is generated in memory and
never printed or saved. The tests generate a separate fictional owner password.

### Individual commands for troubleshooting

These are alternatives to the combined runner, not extra commands you must run
after a successful full check:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test
node core/ui_frontend_tests.cjs
node facilities/frontend_tests.cjs
node emergency/frontend_tests.cjs
node emergency/ambulance_frontend_tests.cjs
```

Use a narrow selection while fixing a specific failing test:

```powershell
.\.venv\Scripts\python.exe manage.py test core.test_workflows core.test_database --verbosity 2
.\.venv\Scripts\python.exe manage.py test --tag workflow
.\.venv\Scripts\python.exe manage.py test --tag database
.\.venv\Scripts\python.exe manage.py test accounts.tests.RegistrationTests
```

The first command runs all 14 new tests. The workflow tag selects 5; the database
tag selects 9. The tags are attached to the new classes, not the earlier tests.
For the full project, always use `manage.py test` or the combined runner; listing
only the four feature apps would omit `core`'s shared and cross-app tests.

### Migrations, admin and development server

No new migration or superuser is needed for Step 9. The drift check should say
`No changes detected`; it does not generate migration files. If you are setting
up a separate copy with the earlier migrations not yet applied, use:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

The tests do not seed the normal database or create a real operator account.
Continue using your existing admin account for manual review. Only if you have
not created one in that copy, run:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

To open the app normally:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Use the existing server if port 8000 is occupied. Open
[MEDTAP](http://127.0.0.1:8000/) or [Django admin](http://127.0.0.1:8000/admin/).
The website looks the same as Step 8; this step improves verification.

## What is covered across the project

| Area | Django tests | Main behaviors checked |
| --- | ---: | --- |
| Accounts | 34 | Registration/password hashing, same-account sign-in, redirects, logout, CSRF, profile/contact ownership, validation, primary switching, escaping and atomic rollback. |
| Facilities | 51 | Model validation, fake seeding/idempotency, admin permissions/CSRF, Haversine boundaries, filters, pagination, HTML/API agreement and safe map data. |
| Emergency and ambulance | 56 | Owned SOS records, retry IDs, location validation, manual share links, private responses, operator roles, transition order, stale versions, rollback and status redaction. |
| First aid | 28 | Source metadata, publication gates, future dates, numbered steps, seed preservation, public HTML/API behavior and admin validation. |
| Core | 23 | Nine existing shared UI/error tests plus five cross-app workflows and nine database-invariant tests. |
| **Total** | **192** | Positive workflows, invalid input, ownership/permission failures and persistence invariants. |

| JavaScript area | Checks | Main behaviors checked |
| --- | ---: | --- |
| Shared UI | 9 | Keyboard menu behavior, error focus, password toggle and selected contrast pairs. |
| Facilities | 9 | GPS success/denial/timeout, coordinate validity, manual/list fallback, safe map popup text. |
| SOS | 12 | CSRF POST, duplicate taps, retry UUID, auth/network failure, redirect safety, copy fallback and notice dismissal. |
| Ambulance | 8 | Read-only polling, hidden tabs, completion/error stopping, safe facility text and manual refresh fallback. |
| **Total** | **38** | Isolated script behavior with mocked browser interfaces. |

This is a behavior inventory, not a statement of 100% line coverage. The tests
use SQLite here. No true concurrent PostgreSQL transactions, PostGIS queries,
real SMS/WhatsApp delivery, ambulance dispatch or production hosting is tested.
The race tests from Step 6 simulate a failed conditional update and rollback;
they do not prove multi-process database behavior. Browser layout checks were
recorded in Step 8; the test client and Node checks do not render a browser.

## Read one test like a viva answer

### The complete workflow

The test creates a `Client(enforce_csrf_checks=True)` and fetches the actual
registration form to obtain its CSRF cookie. It submits the registration form,
then uses the rotated token for the private profile and contact forms. It stores
a synthetic zero-coordinate SOS, retries the same UUID, and confirms that only
one emergency record exists.

It reviews transport with GET, confirms that GET created nothing, then submits
POST twice and confirms one transport record. A separate fictional operator
client updates Requested → Accepted → On the way → Completed with each current
version. The owner's JSON poll confirms the status and excludes internal notes.
Finally, the owner logs out and signs in again through the real login view; the
profile and completed project request remain available to that same account.

The operator is authenticated using Django's `force_login` fixture helper. That
shortcut applies only inside the test database; the owner's registration and
login use actual form submissions. These are in-process HTTP integration tests,
not an automated browser, GPS permission test or real dispatch exercise.

### Database tests versus form validation

Existing model/form tests exercise `full_clean()` and friendly validation
messages. The new tests intentionally call `objects.create()` directly, then
expect `IntegrityError` for rules that have database constraints. This proves
the migrations actually installed the constraints; it would catch accidentally
removing a constraint even if the Python validator still passed its own tests.

Each expected database failure is inside a nested `transaction.atomic()` block.
The exception rolls back that savepoint before the outer test queries again.
Without the nested block, a failed write can leave the test transaction unusable.

Model `save()` does not automatically call `full_clean()`; validation and database
constraints protect different layers. Not every model choice or text rule is a
database constraint. These tests only claim the invariants explicitly checked.
See [Django model validation](https://docs.djangoproject.com/en/6.1/ref/models/instances/#validating-objects).

### Isolation and realistic scope

Django's `TestCase` isolates test changes and the test runner creates a separate
database. In this workspace's SQLite configuration the run uses a temporary
in-memory test database, then destroys it. Fictional profiles/contacts, all-zero
dummy phones and coordinates 0,0 never become normal app records. Source links
under `example.invalid` are fixture strings; tests do not fetch those links.
See [Django's test database explanation](https://docs.djangoproject.com/en/6.1/topics/testing/overview/#the-test-database).

The deletion test documents the current model behavior: profile/contact rows
cascade, while SOS ownership and status-event actors become NULL. Emergency
coordinates and transport history remain stored. This is not anonymisation or
a production retention policy, and there is no new account-deletion UI here.

The default Django test client relaxes CSRF checks, so the new workflow client
enables them explicitly. CSRF-enabled HTTP tests complement the existing unit
tests; JavaScript/rendered layout needs its own checks. See
[Django's testing tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/#the-test-client).

## Result recorded for this step

- New focused tests: **14 passed**.
- Full project runner: **all 7 groups passed**, including **192 Django tests**
  and **38 JavaScript checks**.
- Django system checks: **0 issues**. Migration drift: **No changes detected**.
- Normal user records, operator access, `.env`, model definitions and website
  presentation were not changed by this step.

## Complete current files

Create these files at the paths shown above each block. All imports use existing
project dependencies or Python's standard library; no requirements update is needed.

### `core/test_workflows.py`

Five cross-app HTTP regressions, including the complete owner/operator journey with CSRF enforcement.

```python
"""Cross-app HTTP regressions using fictional data and real CSRF checks."""
import secrets
import uuid

from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import Permission
from django.test import Client, TestCase, tag
from django.urls import reverse
from django.utils import timezone

from accounts.models import EmergencyContact, MedicalProfile, User
from emergency.ambulance_services import request_ambulance
from emergency.models import AmbulanceRequest, AmbulanceStatusEvent, EmergencyRequest
from facilities.models import Facility
from firstaid.models import EmergencyHelpline, FirstAidGuide, FirstAidStep


@tag("workflow")
class CrossAppWorkflowTests(TestCase):
    def setUp(self):
        self.browser = Client(enforce_csrf_checks=True)
        self.password = secrets.token_urlsafe(24)

    def csrf_token(self, browser=None):
        browser = browser or self.browser
        return browser.cookies[settings.CSRF_COOKIE_NAME].value

    def post(self, name, data=None, *, browser=None, kwargs=None, **headers):
        browser = browser or self.browser
        return browser.post(
            reverse(name, kwargs=kwargs), data or {},
            HTTP_X_CSRFTOKEN=self.csrf_token(browser), **headers,
        )

    def register(self):
        self.assertEqual(self.browser.get(reverse("accounts:register")).status_code, 200)
        response = self.post("accounts:register", {
            "username": "fake-workflow-owner", "first_name": "FAKE",
            "email": "workflow@example.invalid",
            "password1": self.password, "password2": self.password,
        })
        self.assertRedirects(response, reverse("accounts:profile_edit"), fetch_redirect_response=False)
        return User.objects.get(username="fake-workflow-owner")

    def operator_browser(self):
        operator = User.objects.create_user(username="fake-workflow-operator", is_staff=True)
        operator.user_permissions.add(*Permission.objects.filter(
            content_type__app_label="emergency",
            codename__in=["view_ambulancerequest", "change_ambulancerequest"],
        ))
        browser = Client(enforce_csrf_checks=True)
        # This shortcut is limited to the operator fixture; owner auth is exercised through HTTP.
        browser.force_login(operator)
        return operator, browser

    def test_registration_to_completed_transport_and_sign_in_again(self):
        owner = self.register()
        self.assertEqual(self.browser.session[SESSION_KEY], str(owner.pk))
        self.assertTrue(owner.check_password(self.password))
        self.assertFalse(owner.is_staff)
        response = self.post("accounts:profile_edit", {
            "blood_group": "O+", "allergies": "FAKE allergy marker",
            "medical_conditions": "FAKE condition marker",
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        response = self.post("accounts:contact_add", {
            "name": "FAKE workflow contact", "relationship": "Friend",
            "phone": "0000000000", "is_primary": "on",
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        profile = MedicalProfile.objects.get(user=owner)
        self.assertEqual(profile.blood_group, "O+")
        self.assertEqual(profile.emergency_contacts.get().phone, "0000000000")

        # Zero is a valid synthetic coordinate; no device location or external service is used.
        payload = {"request_id": str(uuid.uuid4()), "latitude": "0", "longitude": "0"}
        response = self.post("emergency:create", payload, HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 201)
        sos = EmergencyRequest.objects.get(pk=payload["request_id"], user=owner)
        detail_url = reverse("emergency:detail", kwargs={"pk": sos.pk})
        self.assertEqual(response.json(), {"url": detail_url, "created": True})
        retry = self.post("emergency:create", payload, HTTP_ACCEPT="application/json")
        self.assertEqual(retry.status_code, 200)
        self.assertFalse(retry.json()["created"])
        self.assertEqual(EmergencyRequest.objects.count(), 1)
        detail = self.browser.get(detail_url)
        self.assertContains(detail, "FAKE workflow contact")
        self.assertNotContains(detail, "FAKE allergy marker")
        self.assertNotContains(detail, "FAKE condition marker")

        request_url = reverse("emergency:ambulance_request", kwargs={"pk": sos.pk})
        self.assertEqual(self.browser.get(request_url).status_code, 200)
        self.assertFalse(AmbulanceRequest.objects.exists())
        response = self.post("emergency:ambulance_request", kwargs={"pk": sos.pk})
        ambulance = AmbulanceRequest.objects.get(emergency=sos)
        self.assertRedirects(response, reverse("emergency:ambulance_detail", kwargs={"pk": ambulance.pk}))
        self.post("emergency:ambulance_request", kwargs={"pk": sos.pk})
        self.assertEqual(AmbulanceRequest.objects.count(), 1)

        operator, operator_browser = self.operator_browser()
        update_url = reverse("emergency:operator_update", kwargs={"pk": ambulance.pk})
        self.assertEqual(operator_browser.get(update_url).status_code, 200)
        for version, status in enumerate(("accepted", "on_the_way", "completed")):
            with self.subTest(status=status):
                response = self.post("emergency:operator_update", {
                    "expected_version": version, "status": status,
                    "facility": "", "operator_notes": "FAKE internal workflow marker",
                }, browser=operator_browser, kwargs={"pk": ambulance.pk})
                self.assertRedirects(response, update_url, fetch_redirect_response=False)
                snapshot = self.browser.get(reverse("emergency:ambulance_status", kwargs={"pk": ambulance.pk}))
                self.assertEqual(snapshot.status_code, 200)
                self.assertEqual(snapshot.json()["status"], status)
                self.assertEqual(snapshot.json()["version"], version + 1)
                self.assertIn("no-store", snapshot["Cache-Control"])
                self.assertNotIn("operator_notes", snapshot.json())
                self.assertNotIn(b"FAKE internal workflow marker", snapshot.content)
        events = list(ambulance.status_events.all())
        self.assertEqual([event.status for event in events], ["requested", "accepted", "on_the_way", "completed"])
        self.assertEqual([event.changed_by_id for event in events], [owner.pk, operator.pk, operator.pk, operator.pk])
        sos.refresh_from_db()
        self.assertEqual(sos.status, "active")  # Transport completion does not invent an SOS resolution.

        response = self.post("accounts:logout")
        self.assertRedirects(response, reverse("core:home"))
        self.assertNotIn(SESSION_KEY, self.browser.session)
        self.browser.get(reverse("accounts:login"))
        response = self.post("accounts:login", {
            "username": owner.username, "password": self.password,
            "next": reverse("accounts:profile"),
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        self.assertEqual(self.browser.session[SESSION_KEY], str(owner.pk))
        self.assertContains(self.browser.get(reverse("accounts:profile")), "FAKE allergy marker")
        saved = self.browser.get(reverse("emergency:ambulance_status", kwargs={"pk": ambulance.pk}))
        self.assertEqual(saved.json()["status"], "completed")

    def test_registration_rotates_csrf_and_old_form_cannot_change_medical_profile(self):
        self.browser.get(reverse("accounts:register"))
        guest_token = self.csrf_token()
        owner = self.register()
        self.assertNotEqual(guest_token, self.csrf_token())
        data = {"blood_group": "AB+", "allergies": "FAKE rejected update"}
        response = self.browser.post(reverse("accounts:profile_edit"), data, HTTP_X_CSRFTOKEN=guest_token)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(MedicalProfile.objects.get(user=owner).blood_group, "unknown")
        response = self.post("accounts:profile_edit", data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MedicalProfile.objects.get(user=owner).blood_group, "AB+")

    def test_after_logout_json_save_is_401_and_html_returns_to_a_get_page(self):
        self.register()
        self.post("accounts:logout")
        payload = {"request_id": str(uuid.uuid4()), "latitude": "0", "longitude": "0"}
        response = self.post("emergency:create", payload, HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 401)
        self.assertIn("no-store", response["Cache-Control"])
        response = self.post("emergency:create", payload)
        self.assertRedirects(
            response, reverse("accounts:login") + "?next=" + reverse("emergency:start"),
            fetch_redirect_response=False,
        )
        self.assertFalse(EmergencyRequest.objects.exists())

    def test_revoking_operator_permission_blocks_an_already_signed_in_operator(self):
        owner = self.register()
        sos = EmergencyRequest.objects.create(user=owner, latitude=0, longitude=0)
        ambulance, _ = request_ambulance(user=owner, emergency_pk=sos.pk)
        operator, browser = self.operator_browser()
        url = reverse("emergency:operator_update", kwargs={"pk": ambulance.pk})
        self.assertEqual(browser.get(url).status_code, 200)
        operator.user_permissions.remove(Permission.objects.get(
            content_type__app_label="emergency", codename="change_ambulancerequest",
        ))
        self.assertEqual(browser.get(url).status_code, 403)
        response = self.post("emergency:operator_update", {
            "expected_version": 0, "status": "accepted", "operator_notes": "FAKE forbidden update",
        }, browser=browser, kwargs={"pk": ambulance.pk})
        self.assertEqual(response.status_code, 403)
        ambulance.refresh_from_db()
        self.assertEqual((ambulance.status, ambulance.version, ambulance.operator_notes), ("requested", 0, ""))
        self.assertEqual(AmbulanceStatusEvent.objects.filter(ambulance=ambulance).count(), 1)

    def test_public_apis_stay_public_and_exclude_private_records_in_an_authenticated_session(self):
        owner = self.register()
        profile = MedicalProfile.objects.get(user=owner)
        profile.allergies = "FAKE PRIVATE ALLERGY"
        profile.save()
        EmergencyContact.objects.create(profile=profile, name="FAKE PRIVATE CONTACT", relationship="Friend", phone="0000000000")
        sos = EmergencyRequest.objects.create(user=owner, latitude=0, longitude=0)
        ambulance, _ = request_ambulance(user=owner, emergency_pk=sos.pk)
        ambulance.operator_notes = "FAKE PRIVATE OPERATOR NOTE"
        ambulance.save()
        Facility.objects.create(
            name="FAKE public workflow facility", facility_type="hospital", address="FAKE test address",
            phone="0000000000", latitude=0, longitude=0, demo_key="workflow-public",
        )
        guide = FirstAidGuide.objects.create(
            title="FAKE workflow guide", slug="fake-workflow-guide", summary="Test content only",
            source_url="https://example.invalid/test-source", source_checked_on=timezone.localdate(), is_published=True,
        )
        FirstAidStep.objects.create(guide=guide, position=1, instruction="FAKE test content; not medical guidance")
        EmergencyHelpline.objects.create(
            name="FAKE workflow reference", number="112", region="FAKE test region",
            source_url="https://example.invalid/test-source", verified_on=timezone.localdate(), is_active=True,
        )
        guest = Client(enforce_csrf_checks=True)
        for name, kwargs in (
            ("facilities:nearby_api", None), ("firstaid:guide_list_api", None),
            ("firstaid:guide_detail_api", {"slug": guide.slug}), ("firstaid:helplines_api", None),
        ):
            with self.subTest(endpoint=name):
                signed_in = self.browser.get(reverse(name, kwargs=kwargs))
                anonymous = guest.get(reverse(name, kwargs=kwargs))
                self.assertEqual(signed_in.status_code, 200)
                self.assertEqual(anonymous.status_code, 200)
                self.assertEqual(signed_in.json(), anonymous.json())
                for marker in ("FAKE PRIVATE ALLERGY", "FAKE PRIVATE CONTACT", "FAKE PRIVATE OPERATOR NOTE", str(sos.pk)):
                    self.assertNotIn(marker.encode(), signed_in.content)
```

### `core/test_database.py`

Nine database-invariant tests that deliberately bypass form/model validation and verify savepoint recovery.

```python
"""Prove migrated database invariants, independently of ModelForm/full_clean."""
from django.db import IntegrityError, transaction
from django.test import TestCase, tag

from accounts.models import EmergencyContact, MedicalProfile, User
from emergency.models import AmbulanceRequest, AmbulanceStatusEvent, EmergencyRequest
from facilities.models import Facility
from firstaid.models import EmergencyHelpline, FirstAidGuide, FirstAidStep


@tag("database")
class DatabaseInvariantTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username="fake-constraint-owner")
        cls.profile = MedicalProfile.objects.create(user=cls.owner)
        cls.sos = EmergencyRequest.objects.create(user=cls.owner, latitude=0, longitude=0)

    def test_database_allows_only_one_profile_per_user(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MedicalProfile.objects.create(user=self.owner)
        self.assertEqual(MedicalProfile.objects.filter(user=self.owner).count(), 1)

    def test_primary_contact_constraint_is_scoped_to_each_profile(self):
        values = {"name": "FAKE contact", "relationship": "Friend", "phone": "0000000000"}
        EmergencyContact.objects.create(profile=self.profile, is_primary=True, **values)
        with self.assertRaises(IntegrityError), transaction.atomic():
            EmergencyContact.objects.create(profile=self.profile, is_primary=True, **values)
        EmergencyContact.objects.create(profile=self.profile, is_primary=False, **values)
        other = MedicalProfile.objects.create(user=User.objects.create_user(username="fake-other-profile"))
        EmergencyContact.objects.create(profile=other, is_primary=True, **values)
        self.assertEqual(EmergencyContact.objects.filter(is_primary=True).count(), 2)

    def test_database_rejects_out_of_range_facility_coordinates(self):
        for latitude, longitude in (("90.000001", "0"), ("-90.000001", "0"), ("0", "180.000001"), ("0", "-180.000001")):
            with self.subTest(latitude=latitude, longitude=longitude):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Facility.objects.create(
                        name="FAKE invalid coordinate facility", facility_type="hospital", address="FAKE test address",
                        phone="0000000000", latitude=latitude, longitude=longitude,
                    )
        self.assertFalse(Facility.objects.exists())

    def test_database_rejects_out_of_range_sos_coordinates(self):
        for latitude, longitude in (("90.000001", "0"), ("-90.000001", "0"), ("0", "180.000001"), ("0", "-180.000001")):
            with self.subTest(latitude=latitude, longitude=longitude):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    EmergencyRequest.objects.create(user=self.owner, latitude=latitude, longitude=longitude)
        self.assertEqual(EmergencyRequest.objects.count(), 1)

    def test_database_allows_only_one_transport_per_sos(self):
        first = AmbulanceRequest.objects.create(emergency=self.sos)
        with self.assertRaises(IntegrityError), transaction.atomic():
            AmbulanceRequest.objects.create(emergency=self.sos)
        self.assertEqual(AmbulanceRequest.objects.get(emergency=self.sos), first)

    def test_database_prevents_duplicate_status_events_without_blocking_next_status(self):
        ambulance = AmbulanceRequest.objects.create(emergency=self.sos)
        AmbulanceStatusEvent.objects.create(ambulance=ambulance, status="requested", changed_by=self.owner)
        with self.assertRaises(IntegrityError), transaction.atomic():
            AmbulanceStatusEvent.objects.create(ambulance=ambulance, status="requested", changed_by=self.owner)
        AmbulanceStatusEvent.objects.create(ambulance=ambulance, status="accepted", changed_by=self.owner)
        self.assertEqual(ambulance.status_events.count(), 2)

    def test_firstaid_positions_are_positive_and_unique_within_each_guide(self):
        guide = FirstAidGuide.objects.create(title="FAKE draft guide", slug="fake-constraint-guide", summary="Test only")
        FirstAidStep.objects.create(guide=guide, position=1, instruction="FAKE fixture; not advice")
        for position in (0, 1):
            with self.subTest(position=position):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    FirstAidStep.objects.create(guide=guide, position=position, instruction="FAKE invalid fixture")
        other = FirstAidGuide.objects.create(title="FAKE second draft", slug="fake-other-guide", summary="Test only")
        FirstAidStep.objects.create(guide=other, position=1, instruction="FAKE fixture; not advice")
        self.assertEqual(FirstAidStep.objects.count(), 2)

    def test_helpline_number_uniqueness_is_scoped_to_region(self):
        EmergencyHelpline.objects.create(name="FAKE draft reference", number="112", region="FAKE region A")
        with self.assertRaises(IntegrityError), transaction.atomic():
            EmergencyHelpline.objects.create(name="FAKE duplicate reference", number="112", region="FAKE region A")
        EmergencyHelpline.objects.create(name="FAKE other reference", number="112", region="FAKE region B")
        self.assertEqual(EmergencyHelpline.objects.count(), 2)

    def test_deleting_account_removes_contacts_but_retains_unowned_emergency_history(self):
        EmergencyContact.objects.create(profile=self.profile, name="FAKE disposable contact", relationship="Friend", phone="0000000000")
        ambulance = AmbulanceRequest.objects.create(emergency=self.sos)
        event = AmbulanceStatusEvent.objects.create(ambulance=ambulance, status="requested", changed_by=self.owner)
        self.owner.delete()
        self.assertFalse(MedicalProfile.objects.exists())
        self.assertFalse(EmergencyContact.objects.exists())
        self.sos.refresh_from_db()
        event.refresh_from_db()
        self.assertIsNone(self.sos.user_id)
        self.assertIsNone(event.changed_by_id)
        self.assertTrue(AmbulanceRequest.objects.filter(pk=ambulance.pk).exists())
```

### `scripts/check_project.py`

The platform-independent runner uses the selected Python, a temporary child-process signing key, argument lists and nonzero failure exits.

```python
"""Run the local verification suite with the selected Python interpreter."""
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def main():
    node = shutil.which("node")
    if node is None:
        print("Node.js is required for the JavaScript checks. Install Node.js, then rerun this command.", file=sys.stderr)
        return 1

    # Only child processes receive these test values; .env and the running server are unchanged.
    environment = os.environ.copy()
    environment.update({
        "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
        "DJANGO_DEBUG": "False",
        "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1,testserver",
        "PYTHONUNBUFFERED": "1",
    })
    checks = [
        ("Django configuration", [sys.executable, "manage.py", "check"]),
        ("Migration drift", [sys.executable, "manage.py", "makemigrations", "--check", "--dry-run"]),
        ("Django tests", [sys.executable, "manage.py", "test", "--noinput"]),
        ("Shared UI checks", [node, "core/ui_frontend_tests.cjs"]),
        ("Facility checks", [node, "facilities/frontend_tests.cjs"]),
        ("SOS checks", [node, "emergency/frontend_tests.cjs"]),
        ("Ambulance checks", [node, "emergency/ambulance_frontend_tests.cjs"]),
    ]
    for label, command in checks:
        print(f"\nChecking: {label}", flush=True)
        try:
            result = subprocess.run(command, cwd=ROOT, env=environment, check=False)
        except OSError as error:
            print(f"Could not start {label}: {error}", file=sys.stderr)
            return 1
        if result.returncode:
            print(f"Stopped: {label} failed. Fix the error above, then rerun.", file=sys.stderr)
            return 1
    print("\nAll 7 project check groups passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Stop here

Step 9 is complete. After your **next**, Step 10 will prepare deployment
configuration and explain PythonAnywhere/Render options. No hosting service has
been connected or deployed in this step.
