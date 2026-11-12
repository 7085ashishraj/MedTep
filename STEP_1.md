# Step 1 — Project setup and data models

This step is complete in your MEDTAP workspace. It contains configuration and models
for all four apps. It adds no custom views, forms, API endpoints, or templates.
Stop here until you are ready to say **next**.

## Short project plan

1. **Now:** virtual environment, configuration, four apps, database models, migrations.
2. Registration, login/logout, medical profile and emergency contact forms.
3. Facilities admin and a management command containing explicitly FAKE sample facilities.
4. Location permission, Haversine nearby search, filters, list and Leaflet/OpenStreetMap map.
5. SOS record creation and an encoded WhatsApp/SMS message with a Google Maps location link.
6. Ambulance request flow and staff-only status updates.
7. Reviewed first-aid guides and region-specific, verified helpline records.
8. Bootstrap 5 mobile polish and prominent red SOS control.
9. Model, view, permission and API tests.
10. Deployment notes for PythonAnywhere or Render.

We will use function-based HTML views consistently, app-level URL modules, validated
Django forms, CSRF protection for POSTs, and authentication/ownership checks where
required. A small DRF layer will reuse the same models and service functions.
Later apps will gain forms.py, views.py, tests, and API modules when their feature is
implemented. SOS sharing will live in a service function so a messaging provider can
be added later. Session authentication is configured now; mobile-app authentication
will be chosen when that client exists.

## Complete current folder structure

```text
MEDTAP/
|-- .env                        # local secret; never commit or share
|-- .env.example                # safe configuration example
|-- .gitignore
|-- .venv/                      # project virtual environment, ignored
|-- .python/                    # project-local Python installed by uv, ignored
|-- .uv-cache/                  # tooling cache and temporary verification, ignored
|-- README.md
|-- STEP_1.md                   # this tutorial
|-- requirements.txt
|-- manage.py
|-- db.sqlite3                  # local database, ignored
|-- config/
|   |-- __init__.py
|   |-- settings.py
|   |-- urls.py
|   |-- asgi.py
|   `-- wsgi.py
|-- common/                     # shared Python package, not an installed Django app
|   |-- __init__.py
|   |-- models.py
|   `-- validators.py
|-- accounts/
|   |-- __init__.py
|   |-- apps.py
|   |-- admin.py
|   |-- models.py
|   |-- urls.py
|   `-- migrations/
|       |-- __init__.py
|       `-- 0001_initial.py
|-- facilities/
|   |-- __init__.py
|   |-- apps.py
|   |-- models.py
|   |-- urls.py
|   `-- migrations/
|       |-- __init__.py
|       `-- 0001_initial.py
|-- emergency/
|   |-- __init__.py
|   |-- apps.py
|   |-- models.py
|   |-- urls.py
|   `-- migrations/
|       |-- __init__.py
|       `-- 0001_initial.py
`-- firstaid/
    |-- __init__.py
    |-- apps.py
    |-- models.py
    |-- urls.py
    `-- migrations/
        |-- __init__.py
        `-- 0001_initial.py
```

Python also generates __pycache__ directories; they are ignored. Global templates/
and static/ directories will be added with the UI. STATIC_ROOT is for deployment's
collected static files, not for writing source CSS.

## Environment and versions

Your workspace is Windows/PowerShell. Python 3.11 was installed outside PATH; it
cannot run the requested current Django release. I installed **Python 3.14.7 locally
inside this project**, created .venv, and installed the pinned dependencies.

As checked on November 10, 2026, the latest stable Django is **6.1.3**, requiring
Python 3.12 or newer. See [Django on PyPI](https://pypi.org/project/Django/).
DRF declares support for Django 6.1 in its
[official requirements](https://www.django-rest-framework.org/#requirements).
The installed versions are recorded in requirements.txt below.

In VS Code, use **Python: Select Interpreter** and select:

```text
C:\Users\Ashish\OneDrive\Desktop\MEDTAP\.venv\Scripts\python.exe
```

### Commands for this already-prepared workspace

Open a PowerShell terminal in VS Code. These commands use the environment's Python
explicitly, so activation and execution-policy changes are unnecessary.

```powershell
Set-Location 'C:\Users\Ashish\OneDrive\Desktop\MEDTAP'
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m django --version
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations accounts facilities emergency firstaid
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

The environment, .env, migrations and database already exist. Rerunning migration
commands is safe: expect **No changes detected** and **No migrations to apply**.
Choose your own superuser username and password when prompted. The password is not
displayed as you type. I have not created a superuser or chosen credentials for you.
Stop runserver with Ctrl+C.

Expected version output:

```text
Python 3.14.7
6.1.3
```

Expected check/server output includes:

```text
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8000/
```

Open http://127.0.0.1:8000/admin/ and log in. Only Users and Groups are registered
currently. Facility and other domain admin screens will be added in their steps.
The root URL http://127.0.0.1:8000/ returns **404**, as do the empty app URL prefixes;
this is expected before we create pages. Do not expect a home page yet.

### Recreating the environment on another Windows computer

Use this section only when you do not already have .venv. Install Python 3.14 from
[python.org](https://www.python.org/downloads/windows/) first. Save the source files
below in the shown structure, then run these commands from the project root:

```powershell
py -3.14 --version
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create .env with a unique random secret. This command deliberately leaves an
existing .env unchanged and does not print its secret:

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from django.core.management.utils import get_random_secret_key; p = Path('.env'); p.exists() or p.write_text('DJANGO_SECRET_KEY=' + get_random_secret_key() + '\nDJANGO_DEBUG=True\nDJANGO_ALLOWED_HOSTS=127.0.0.1,localhost\n', encoding='utf-8')"
```

If you manually copied .env.example first, its secret is empty. Open .env, remove
that empty DJANGO_SECRET_KEY line, and generate a value locally with the following
command, then paste the result into that line. Never share that result:

```powershell
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then run check, makemigrations, migrate, createsuperuser and runserver as above.
Do not migrate before configuring AUTH_USER_MODEL and creating accounts' initial
migration. Django's custom user must be present in the app's first migration.
See [Django's custom-user guidance](https://docs.djangoproject.com/en/6.1/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project).

If you use optional PowerShell activation, the command is:

```powershell
.\.venv\Scripts\Activate.ps1
```

If your execution policy blocks it, keep using the explicit Python commands above.
You do not need to change the system execution policy.

## Model design: viva explanations

| App/package | Models | Purpose |
| --- | --- | --- |
| common | TimeStampedModel (abstract) | Reuses created_at/updated_at without creating a separate table. |
| accounts | User, MedicalProfile, EmergencyContact | Keeps credentials separate from medical details; a profile has many contacts. |
| facilities | Facility, Speciality | Stores hospitals, clinics, pharmacies and blood banks; each can have many specialities. |
| emergency | EmergencyRequest, AmbulanceRequest | Records an SOS location; an SOS can have at most one ambulance request. |
| firstaid | FirstAidGuide, FirstAidStep, EmergencyHelpline | Stores draft guides with ordered steps and region-specific helpline records. |

- **Custom User:** inherits Django's password hashing and authentication. Configuring
  it now avoids a difficult user-table replacement after migrations exist.
- **OneToOneField:** a user has at most one medical profile. Profiles are not created
  by a signal. Step 2 will create/update them explicitly during registration/profile
  handling; a newly created superuser currently has no profile.
- **ForeignKey:** multiple contacts belong to one profile. A conditional unique
  constraint permits at most one primary contact; it does not require one.
- **ManyToManyField:** a facility can have multiple specialities, and one speciality
  can belong to many facilities. Django creates the join table.
- **Coordinates:** latitude ranges from -90 to 90 and longitude from -180 to 180.
  Decimal fields store six fractional digits. Validators help forms report errors;
  database check constraints also reject out-of-range writes that bypass forms.
- **Phone fields are strings:** this preserves leading zeroes and an optional +.
  Validation checks format only, not whether a number exists. Helplines allow short
  codes, while contact/facility numbers require 7 to 15 digits.
- **Choices:** named values avoid spelling mistakes in forms. Ambulance statuses are
  requested, accepted, on_the_way, completed. The ordered transition rules and staff
  permissions will be implemented in Step 6; a choices field alone is not a workflow.
- **UUID SOS primary key:** gives each request an unpredictable identifier. It is not
  access control: later views/API still must check ownership and staff permissions.
- **Deletion:** removing a user removes their medical profile and contacts. The SOS
  history remains with user=NULL. Deleting a facility leaves its ambulance history
  with facility=NULL. Removing an SOS also removes its linked ambulance request.
  A production retention/anonymization policy will need separate design.
- **Timestamps:** created_at is set on creation and updated_at on ordinary save().
  QuerySet.update() bypasses auto_now; later status services should use save().
- **First aid:** guides start unpublished, with source/review fields. Helplines start
  inactive, with region/source/verification fields. No medical instructions or phone
  records are seeded now. Empty allergy text means unrecorded, not no allergies.
- **Database portability:** these models use ordinary Django fields/relations rather
  than SQLite-specific SQL. PostgreSQL can use this schema. Moving existing data
  requires a separate migration/import plan. PostGIS will additionally require GIS
  dependencies, a PointField data migration and spatial indexing. Haversine search
  comes in Step 4; the present index helps type/active filtering, not spatial search.
- **Validation:** Django ModelForms validate models. Direct model save() does not
  automatically run full_clean(); service code must validate its inputs. Later DRF
  serializers will validate request data explicitly, including any cross-field rules.
  See [Django model validation](https://docs.djangoproject.com/en/6.1/ref/models/instances/#validating-objects).
- **Secrets:** python-decouple reads .env; real process environment variables take
  precedence. Names use DJANGO_ to avoid collision with the host's DEBUG=release.
  DEBUG defaults to False, the secret has no fallback, and CSRF middleware is enabled.
  This is local configuration; deployment security settings come in Step 10.

**Disclaimer for the future shared UI:** “This app does not replace calling 112 in a
real emergency. SOS and ambulance requests in this demo do not contact emergency
services or dispatch an ambulance.” It will be visible in the shared base template
when templates are introduced. It is documented now; no public UI exists yet.

## Complete source code, file by file

The source files are already saved in the workspace. The following blocks are also
complete and can be copied to recreate them. Do not replace .env with .env.example;
the example deliberately has no usable secret.

### requirements.txt

Pinned versions make installation reproducible for the three libraries we use directly.

```text
Django==6.1.3
djangorestframework==3.18.3
python-decouple==3.8
```

### .gitignore

Keeps secrets, the virtual environment, local databases and generated files out of Git.
Commit source code and migration files instead.

```text
.venv/
.python/
.uv-cache/
.env
.env.*
!.env.example
__pycache__/
*.py[cod]
*.sqlite3
*.sqlite3-*
staticfiles/
media/
.coverage
htmlcov/
.pytest_cache/
.vscode/
```

### .env.example

Documents the required settings without including an actual secret. The real .env
stays on your computer. DJANGO_DEBUG=True is for local development only.

```text
# Generate a unique DJANGO_SECRET_KEY using the command in STEP_1.md.
DJANGO_SECRET_KEY=
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

### manage.py

The command-line entry point loads this project's settings before running Django commands.

```python
#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

### config/__init__.py

Create this as an empty file. It marks a Python package.

```python

```

### config/settings.py

Connects the apps, middleware, SQLite database, custom user, templates engine and DRF.
The template engine is configured in advance; we are not creating templates yet.
Session authentication and authenticated API defaults provide a starting point;
public facility/guide endpoints will get explicit permissions when added.

```python
from pathlib import Path

from decouple import AutoConfig, Csv

BASE_DIR = Path(__file__).resolve().parent.parent
env = AutoConfig(search_path=str(BASE_DIR))

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "accounts.apps.AccountsConfig",
    "facilities.apps.FacilitiesConfig",
    "emergency.apps.EmergencyConfig",
    "firstaid.apps.FirstaidConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
```

### config/urls.py

Delegates URLs to each app, so app routes remain independent. Only Django's built-in
admin has a working page now. The namespaced app URL lists are empty placeholders.

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("facilities/", include("facilities.urls")),
    path("emergency/", include("emergency.urls")),
    path("first-aid/", include("firstaid.urls")),
]
```

### config/asgi.py

Exposes the application to an ASGI-compatible server, which supports asynchronous hosting.

```python
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_asgi_application()
```

### config/wsgi.py

Exposes the application to a WSGI-compatible server, commonly used for Django deployment.

```python
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
```

### common/__init__.py

Create this as an empty file. It marks a Python package.

```python

```

### common/models.py

An abstract base model shares timestamp fields; each concrete subclass gets its own columns.

```python
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

### common/validators.py

Reusable format and coordinate validators keep the same rules across multiple apps.

```python
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

phone_validator = RegexValidator(
    regex=r"\A\+?[0-9]{7,15}\Z",
    message="Enter 7 to 15 digits, optionally starting with +; omit spaces.",
)
latitude_validators = [
    MinValueValidator(Decimal("-90")),
    MaxValueValidator(Decimal("90")),
]
longitude_validators = [
    MinValueValidator(Decimal("-180")),
    MaxValueValidator(Decimal("180")),
]
```

### accounts/__init__.py

Create this as an empty file. It marks a Python package.

```python

```

### accounts/apps.py

Registers the app's Python package and default primary-key field type with Django.

```python
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
```

### accounts/models.py

Defines authentication, private medical information and related contacts. A medical
profile belongs to exactly one user, and each contact belongs to one profile.

```python
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import TimeStampedModel
from common.validators import phone_validator


class User(AbstractUser):
    """Keep Django authentication; allow future user fields without replacing it."""


class MedicalProfile(TimeStampedModel):
    class BloodGroup(models.TextChoices):
        UNKNOWN = "unknown", "Unknown"
        A_POSITIVE = "A+", "A positive"
        A_NEGATIVE = "A-", "A negative"
        B_POSITIVE = "B+", "B positive"
        B_NEGATIVE = "B-", "B negative"
        AB_POSITIVE = "AB+", "AB positive"
        AB_NEGATIVE = "AB-", "AB negative"
        O_POSITIVE = "O+", "O positive"
        O_NEGATIVE = "O-", "O negative"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_profile",
    )
    blood_group = models.CharField(
        max_length=7, choices=BloodGroup.choices, default=BloodGroup.UNKNOWN,
    )
    allergies = models.TextField(blank=True, help_text="Blank means not recorded.")
    medical_conditions = models.TextField(blank=True)

    def __str__(self):
        return f"Medical profile for {self.user.username}"


class EmergencyContact(TimeStampedModel):
    profile = models.ForeignKey(
        MedicalProfile, on_delete=models.CASCADE, related_name="emergency_contacts",
    )
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=16, validators=[phone_validator])
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "name", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile"],
                condition=models.Q(is_primary=True),
                name="one_primary_contact_per_profile",
            ),
        ]

    def __str__(self):
        return self.name
```

### accounts/admin.py

Uses Django's existing UserAdmin so the custom user has normal password and permission
management. Domain admin screens are deferred to their corresponding features.

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

admin.site.register(User, UserAdmin)
```

### accounts/urls.py

Reserves the accounts URL namespace; registration and login routes arrive in Step 2.

```python
app_name = "accounts"
urlpatterns = []
```

### accounts/migrations/__init__.py

Create this as an empty file. It marks a Python package.

```python

```

### facilities/__init__.py

Create this as an empty file. It marks a Python package.

```python

```

### facilities/apps.py

Registers the facilities app and its default primary-key field type.

```python
from django.apps import AppConfig


class FacilitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "facilities"
```

### facilities/models.py

Stores filterable facility types, addresses, contact numbers, coordinates and specialities.
is_active allows an administrator to hide a facility without deleting its record.

```python
from django.db import models

from common.models import TimeStampedModel
from common.validators import latitude_validators, longitude_validators, phone_validator


class Speciality(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "specialities"

    def __str__(self):
        return self.name


class Facility(TimeStampedModel):
    class Type(models.TextChoices):
        HOSPITAL = "hospital", "Hospital"
        CLINIC = "clinic", "Clinic"
        PHARMACY = "pharmacy", "Pharmacy"
        BLOOD_BANK = "blood_bank", "Blood bank"

    name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=20, choices=Type.choices)
    specialities = models.ManyToManyField(
        Speciality, blank=True, related_name="facilities",
    )
    address = models.TextField()
    phone = models.CharField(max_length=16, validators=[phone_validator])
    latitude = models.DecimalField(
        max_digits=8, decimal_places=6, validators=latitude_validators,
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, validators=longitude_validators,
    )
    is_24x7 = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name", "pk"]
        indexes = [models.Index(fields=["facility_type", "is_active"])]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    latitude__gte=-90, latitude__lte=90,
                    longitude__gte=-180, longitude__lte=180,
                ),
                name="facility_valid_coordinates",
            ),
        ]

    def __str__(self):
        return self.name
```

### facilities/urls.py

Reserves the facilities namespace for the search and detail pages added later.

```python
app_name = "facilities"
urlpatterns = []
```

### facilities/migrations/__init__.py

Create this as an empty file. It marks a Python package.

```python

```

### emergency/__init__.py

Create this as an empty file. It marks a Python package.

```python

```

### emergency/apps.py

Registers the emergency app and its default primary-key field type.

```python
from django.apps import AppConfig


class EmergencyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "emergency"
```

### emergency/models.py

An SOS stores the captured coordinates. Its optional ambulance request references
the same incident, avoiding a second, potentially inconsistent location copy.
A facility association records the provider selected later in the request workflow.

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

    class Meta:
        ordering = ["-created_at", "pk"]
        indexes = [models.Index(fields=["status", "created_at"])]

    def __str__(self):
        return f"Ambulance for {self.emergency_id} ({self.get_status_display()})"
```

### emergency/urls.py

Reserves the emergency namespace for authenticated SOS and ambulance actions.

```python
app_name = "emergency"
urlpatterns = []
```

### emergency/migrations/__init__.py

Create this as an empty file. It marks a Python package.

```python

```

### firstaid/__init__.py

Create this as an empty file. It marks a Python package.

```python

```

### firstaid/apps.py

Registers the first-aid app and its default primary-key field type.

```python
from django.apps import AppConfig


class FirstaidConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "firstaid"
```

### firstaid/models.py

Keeps steps in display order and reserves source/review metadata for guide content.
Helplines support short numbers and regional verification without assuming every
ambulance code works everywhere. Records remain drafts/inactive until reviewed.

```python
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from common.models import TimeStampedModel


class FirstAidGuide(TimeStampedModel):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    summary = models.TextField()
    source_url = models.URLField(blank=True)
    reviewed_on = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["title", "pk"]

    def __str__(self):
        return self.title


class FirstAidStep(models.Model):
    guide = models.ForeignKey(
        FirstAidGuide, on_delete=models.CASCADE, related_name="steps",
    )
    position = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    instruction = models.TextField()

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["guide", "position"], name="unique_position_per_guide",
            ),
            models.CheckConstraint(
                condition=models.Q(position__gte=1), name="firstaid_positive_position",
            ),
        ]

    def __str__(self):
        return f"{self.guide.title}: step {self.position}"


class EmergencyHelpline(TimeStampedModel):
    name = models.CharField(max_length=100)
    number = models.CharField(
        max_length=16,
        validators=[RegexValidator(r"\A\+?[0-9]{2,15}\Z", "Enter 2 to 15 digits; optional +.")],
    )
    region = models.CharField(max_length=100, help_text="Country, state, or service area.")
    description = models.TextField(blank=True)
    source_url = models.URLField(blank=True)
    verified_on = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["region", "name", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["number", "region"], name="unique_helpline_number_per_region",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.number})"
```

### firstaid/urls.py

Reserves the namespace for guide and helpline pages introduced in Step 7.

```python
app_name = "firstaid"
urlpatterns = []
```

### firstaid/migrations/__init__.py

Create this as an empty file. It marks a Python package.

```python

```

## Generated migrations

`makemigrations` already generated the following files, and `migrate` applied them.
Keep them in version control. They describe the database changes and allow a fresh
installation to recreate the schema. You normally generate migrations rather than
handwriting or editing these blocks; they are included for a complete source snapshot.

### accounts/migrations/0001_initial.py

```python
# Generated by Django 6.1.3 on 2026-11-10 07:00

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='MedicalProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('blood_group', models.CharField(choices=[('unknown', 'Unknown'), ('A+', 'A positive'), ('A-', 'A negative'), ('B+', 'B positive'), ('B-', 'B negative'), ('AB+', 'AB positive'), ('AB-', 'AB negative'), ('O+', 'O positive'), ('O-', 'O negative')], default='unknown', max_length=7)),
                ('allergies', models.TextField(blank=True, help_text='Blank means not recorded.')),
                ('medical_conditions', models.TextField(blank=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='medical_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmergencyContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('relationship', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=16, validators=[django.core.validators.RegexValidator(message='Enter 7 to 15 digits, optionally starting with +; omit spaces.', regex='\\A\\+?[0-9]{7,15}\\Z')])),
                ('is_primary', models.BooleanField(default=False)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emergency_contacts', to='accounts.medicalprofile')),
            ],
            options={
                'ordering': ['-is_primary', 'name', 'pk'],
                'constraints': [models.UniqueConstraint(condition=models.Q(('is_primary', True)), fields=('profile',), name='one_primary_contact_per_profile')],
            },
        ),
    ]
```

### facilities/migrations/0001_initial.py

```python
# Generated by Django 6.1.3 on 2026-11-10 07:00

import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Speciality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name_plural': 'specialities',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('facility_type', models.CharField(choices=[('hospital', 'Hospital'), ('clinic', 'Clinic'), ('pharmacy', 'Pharmacy'), ('blood_bank', 'Blood bank')], max_length=20)),
                ('address', models.TextField()),
                ('phone', models.CharField(max_length=16, validators=[django.core.validators.RegexValidator(message='Enter 7 to 15 digits, optionally starting with +; omit spaces.', regex='\\A\\+?[0-9]{7,15}\\Z')])),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('-90')), django.core.validators.MaxValueValidator(Decimal('90'))])),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9, validators=[django.core.validators.MinValueValidator(Decimal('-180')), django.core.validators.MaxValueValidator(Decimal('180'))])),
                ('is_24x7', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('specialities', models.ManyToManyField(blank=True, related_name='facilities', to='facilities.speciality')),
            ],
            options={
                'ordering': ['name', 'pk'],
                'indexes': [models.Index(fields=['facility_type', 'is_active'], name='facilities__facilit_735223_idx')],
                'constraints': [models.CheckConstraint(condition=models.Q(('latitude__gte', -90), ('latitude__lte', 90), ('longitude__gte', -180), ('longitude__lte', 180)), name='facility_valid_coordinates')],
            },
        ),
    ]
```

### emergency/migrations/0001_initial.py

```python
# Generated by Django 6.1.3 on 2026-11-10 07:00

import django.core.validators
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('facilities', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmergencyRequest',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('-90')), django.core.validators.MaxValueValidator(Decimal('90'))])),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9, validators=[django.core.validators.MinValueValidator(Decimal('-180')), django.core.validators.MaxValueValidator(Decimal('180'))])),
                ('status', models.CharField(choices=[('active', 'Active'), ('resolved', 'Resolved'), ('cancelled', 'Cancelled')], default='active', max_length=10)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='emergency_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at', 'pk'],
            },
        ),
        migrations.CreateModel(
            name='AmbulanceRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('requested', 'Requested'), ('accepted', 'Accepted'), ('on_the_way', 'On the way'), ('completed', 'Completed')], default='requested', max_length=20)),
                ('operator_notes', models.TextField(blank=True)),
                ('facility', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ambulance_requests', to='facilities.facility')),
                ('emergency', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ambulance_request', to='emergency.emergencyrequest')),
            ],
            options={
                'ordering': ['-created_at', 'pk'],
            },
        ),
        migrations.AddIndex(
            model_name='emergencyrequest',
            index=models.Index(fields=['status', 'created_at'], name='emergency_e_status_f336d2_idx'),
        ),
        migrations.AddConstraint(
            model_name='emergencyrequest',
            constraint=models.CheckConstraint(condition=models.Q(('latitude__gte', -90), ('latitude__lte', 90), ('longitude__gte', -180), ('longitude__lte', 180)), name='emergency_valid_coordinates'),
        ),
        migrations.AddIndex(
            model_name='ambulancerequest',
            index=models.Index(fields=['status', 'created_at'], name='emergency_a_status_928c47_idx'),
        ),
    ]
```

### firstaid/migrations/0001_initial.py

```python
# Generated by Django 6.1.3 on 2026-11-10 07:00

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FirstAidGuide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=150)),
                ('slug', models.SlugField(max_length=150, unique=True)),
                ('summary', models.TextField()),
                ('source_url', models.URLField(blank=True)),
                ('reviewed_on', models.DateField(blank=True, null=True)),
                ('is_published', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['title', 'pk'],
            },
        ),
        migrations.CreateModel(
            name='EmergencyHelpline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('number', models.CharField(max_length=16, validators=[django.core.validators.RegexValidator('\\A\\+?[0-9]{2,15}\\Z', 'Enter 2 to 15 digits; optional +.')])),
                ('region', models.CharField(help_text='Country, state, or service area.', max_length=100)),
                ('description', models.TextField(blank=True)),
                ('source_url', models.URLField(blank=True)),
                ('verified_on', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['region', 'name', 'pk'],
                'constraints': [models.UniqueConstraint(fields=('number', 'region'), name='unique_helpline_number_per_region')],
            },
        ),
        migrations.CreateModel(
            name='FirstAidStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('instruction', models.TextField()),
                ('guide', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='firstaid.firstaidguide')),
            ],
            options={
                'ordering': ['position'],
                'constraints': [models.UniqueConstraint(fields=('guide', 'position'), name='unique_position_per_guide'), models.CheckConstraint(condition=models.Q(('position__gte', 1)), name='firstaid_positive_position')],
            },
        ),
    ]
```

## Verification completed

- Installed the pinned dependency versions; pip check reports no broken requirements.
- Django system check reports no issues.
- Generated and applied all initial migrations; migration drift check reports no changes.
- Applied migrations again to a separate temporary database to confirm fresh setup works.
- Checked relationships, phone/coordinate validation, coordinate database constraints,
  one primary contact, one ambulance per SOS, ordered/unique/positive guide steps,
  default draft/inactive records, deletion behavior, and authenticated API defaults.
- Checked the built-in admin login returns HTTP 200 and the intentionally absent home
  page returns HTTP 404.

Temporary checks used only fictional data and did not seed your development database.
A permanent test suite remains scheduled for Step 9. No superuser has been created.

To inspect migration state yourself:

```powershell
.\.venv\Scripts\python.exe manage.py showmigrations accounts facilities emergency firstaid
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pip check
```

Each initial migration should be marked `[X]`. Stop here. Say **next** when you want
Step 2: registration, login, and medical profiles. If anything fails, paste the full
traceback and the command you ran so we can identify the cause.
