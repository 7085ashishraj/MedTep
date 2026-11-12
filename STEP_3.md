# Step 3 — Facilities in Django admin and FAKE sample data

This feature is complete. Hospitals, clinics, pharmacies and blood banks can now
be managed through Django admin. The migration is applied and eight explicitly
FAKE sample facilities plus six specialities are in the development database.
Stop here until you say **next** for nearby search and maps.

## Short plan for this step

1. Register Facility and Speciality with useful admin search, filters and editing.
2. Add a stable optional demo identifier so sample records remain identifiable.
3. Create a repeatable management command with fictional sample data.
4. Verify admin permissions, validation and sample-command behaviour.

## Open the admin

- Facility list: **http://127.0.0.1:8000/admin/facilities/facility/**
- Speciality list: **http://127.0.0.1:8000/admin/facilities/speciality/**
- Admin home: http://127.0.0.1:8000/admin/

**Use an admin account.** A normal account created through the public registration
page does not have staff access. If you have not created an administrator, run:

```powershell
Set-Location 'C:\Users\Ashish\OneDrive\Desktop\MEDTAP'
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Choose your own username and password. Password input is intentionally not shown
as you type. I have not chosen credentials or promoted your public account.
Existing superusers can use their existing credentials. A staff account also needs
model permissions; staff status alone does not grant facility access. Speciality
view permission is needed to use the speciality autocomplete.

The development server is running and was restarted to load the new admin module.
If you need to start it yourself, keep this terminal open:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

## Exact migration, sample-data and test commands

These steps have already been completed in this workspace. On a fresh copy, or
when applying the changed model, run them from MEDTAP:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations facilities
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo_facilities
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test facilities accounts
```

The initial migration file for this change is included below, so makemigrations
reports No changes detected when it already exists. The migration is:

```text
facilities/0002_facility_demo_key
```

On the first seed into a database without samples, expect:

```text
Created 8 FAKE facilities; kept 0 existing demo records. Created 6 specialities.
```

On a second run with all samples present, expect:

```text
Created 0 FAKE facilities; kept 8 existing demo records. Created 0 specialities.
```

Other existing speciality records may reduce the Created specialities count.
The complete current facilities/account test run reports:

```text
Ran 60 tests ...
OK
```

No additional Python package or API key is required.

## What you should see and try

After signing into admin, the Facilities section contains Facilities and
Specialities. The facility list shows name, type, phone, specialities, 24x7, active
and FAKE sample status. There are 25 records per admin page.

1. Use the search box to search names, addresses, phones or speciality names.
   Matching several specialities does not duplicate a facility in the results.
2. Use filters for facility type, 24x7 status, active status, data source and used
   specialities. Data source distinguishes FAKE sample data from ordinary entries;
   an ordinary entry is not automatically a verified facility.
3. Open a sample facility. Edit its name/address, coordinates, phone, specialities
   or flags. Its stable demo key and timestamps are read-only metadata.
4. Change 24x7/active in the list and choose Save. Opening hours are separate from
   active status and do not imply live bed or stock availability.
5. Create a Speciality. Django admin suggests its slug from the name. You can edit
   that slug before saving, subject to uniqueness validation.
6. Create a facility and select multiple specialities with autocomplete. Enter
   decimal latitude/longitude and a phone with 7–15 digits, optional +, no spaces.
7. Try a latitude of 91 or longitude of 181. Expect field validation errors and no
   saved invalid row. Use fictional values when practicing.
8. Rerun the seed command after changing a demo name or speciality selection.
   Expect your edits to remain and no duplicate demo facility.
9. Deleting a facility uses Django admin's confirmation flow. If you delete one of
   the seeded facilities, rerunning the seed recreates that missing demo record.

The public Find Hospitals action remains a search preview. This step does not add
facility listing pages, geolocation search, maps or REST endpoints.

## Sample-data rules

All eight generated facility names start with FAKE. Their addresses are fictional,
all phones are the dummy number **0000000000**, and their coordinate cluster is
synthetic data for later distance-search practice. The positions do not identify
actual healthcare services. Do not call or navigate to these samples.

| Sample | Type | 24x7 | Active |
| --- | --- | --- | --- |
| FAKE Demo Hospital Alpha | Hospital | Yes | Yes |
| FAKE Demo Hospital Beta | Hospital | No | Yes |
| FAKE Demo Clinic Alpha | Clinic | No | Yes |
| FAKE Demo Clinic Beta | Clinic | No | Yes |
| FAKE Demo Pharmacy Alpha | Pharmacy | Yes | Yes |
| FAKE Demo Pharmacy Beta | Pharmacy | No | No |
| FAKE Demo Blood Bank Alpha | Blood bank | Yes | Yes |
| FAKE Demo Blood Bank Beta | Blood bank | No | Yes |

Speciality labels are general service terms, not claims about real providers.
The command reuses an existing speciality with a matching slug, or matching name,
without renaming it. It adds only missing demo facilities and never resets existing
facility fields or speciality assignments. Deleted associations on existing demo
records are therefore not repaired automatically; preserving admin edits wins.

Future public listings must clearly mark is_demo records and prevent dummy phone
calls/directions from being presented as real services. Nearby search is the next
feature and must use these markers. The public emergency disclaimer is retained.

## Files added or changed

```text
MEDTAP/
|-- facilities/
|   |-- models.py
|   |-- admin.py
|   |-- sample_data.py
|   |-- tests.py
|   |-- management/
|   |   |-- __init__.py
|   |   `-- commands/
|   |       |-- __init__.py
|   |       `-- seed_demo_facilities.py
|   `-- migrations/
|       `-- 0002_facility_demo_key.py
|-- README.md
`-- STEP_3.md
```

Existing auth, medical profiles and emergency contacts are not changed by seeding.
No real user credentials or patient records are included in sample data.

## Viva explanations

- **ModelAdmin:** Django builds internal management forms from model metadata.
  Registering each model in admin.py exposes it to authorised administrators.
  ModelAdmin's fieldsets, list_display, list_filter and search_fields organise the UI.
- **Validation:** the generated admin ModelForm runs model field validation, including
  phone/coordinate validators. Database constraints additionally protect coordinate
  bounds. A separate custom forms.py is unnecessary for these standard admin forms.
- **Many-to-many:** facilities share specialities through Django's join table.
  autocomplete_fields uses SpecialityAdmin.search_fields to find options. The admin
  queryset prefetches specialities so showing names avoids one query per facility.
- **Internal permissions:** Django admin checks staff status and model permissions.
  CSRF protects modifying requests. Delete links ask for confirmation before the
  actual POST deletion; no custom permission bypass is added.
- **demo_key:** an optional, unique, non-editable slug identifies seeded samples even
  after a name change. is_demo is a computed property, not a second stored flag.
  Ordinary rows have demo_key=NULL. A nullable unique string is deliberate here:
  multiple ordinary rows can have NULL while populated demo keys remain unique on
  SQLite and PostgreSQL. It is not a GIS or public URL identifier.
- **Migration:** makemigrations records the new field in 0002_facility_demo_key.py;
  migrate applies that schema change. Existing facilities receive NULL, preserving
  their original fields and marking them as ordinary entries.
- **Management command:** Django discovers a Command class in
  management/commands/seed_demo_facilities.py. __init__.py files mark packages.
  stdout.write makes output easy to capture in tests.
- **Idempotence:** the same seed command can run repeatedly without duplicating
  records. Stable unique keys and get_or_create handle identification; the explicit
  existing-row check also preserves human edits and changed speciality relations.
- **Transactions:** all seed writes are in one atomic block. Validation/integrity
  failures roll back the command, including newly created speciality records.
- **Validation in scripts:** ordinary model save does not automatically call
  full_clean. The command explicitly validates new sample objects before saving.
- **Decimal coordinates:** Decimal values retain the intended six fractional digits
  without binary-float artefacts when seeding. Haversine calculations are for the
  next step; this step adds no spatial query or live location claims.
- **Testing:** TestCase uses a separate test database. Tests cover actual admin
  requests, ownership/permissions, validation and seed behaviour without logging
  into your browser or creating real admin accounts in the development database.

See Django's official [admin reference](https://docs.djangoproject.com/en/6.1/ref/contrib/admin/)
and [custom management command guide](https://docs.djangoproject.com/en/6.1/howto/custom-management-commands/).

## Complete code, file by file

The files are already saved in the workspace. Each block below contains the full
current source for this step, including the generated migration.

### facilities/models.py

Existing facility/speciality models plus the optional stable demo key and computed is_demo property.

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
    demo_key = models.SlugField(
        max_length=50, unique=True, null=True, blank=True, editable=False,
        help_text="Stable identifier for generated FAKE sample data; blank for ordinary facilities.",
    )

    @property
    def is_demo(self):
        return self.demo_key is not None

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

### facilities/admin.py

Internal admin screens, filters, search, speciality autocomplete and read-only metadata.

```python
from django.contrib import admin

from .models import Facility, Speciality


class DemoDataFilter(admin.SimpleListFilter):
    title = "data source"
    parameter_name = "demo"

    def lookups(self, request, model_admin):
        return (("yes", "FAKE sample data"), ("no", "Ordinary entries"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(demo_key__isnull=False)
        if self.value() == "no":
            return queryset.filter(demo_key__isnull=True)
        return queryset


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = (
        "name", "facility_type", "phone", "speciality_names", "is_24x7", "is_active", "demo_status",
    )
    list_filter = (
        "facility_type", "is_24x7", "is_active", DemoDataFilter,
        ("specialities", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("name", "address", "phone", "specialities__name")
    autocomplete_fields = ("specialities",)
    list_editable = ("is_24x7", "is_active")
    readonly_fields = ("demo_status", "demo_key", "created_at", "updated_at")
    list_per_page = 25
    ordering = ("name", "pk")
    fieldsets = (
        ("Facility details", {"fields": ("name", "facility_type", "specialities")}),
        ("Contact and location", {
            "fields": ("address", "phone", ("latitude", "longitude")),
            "description": "Use decimal degrees: latitude -90 to 90; longitude -180 to 180. Phone: 7–15 digits, optional +, no spaces.",
        }),
        ("Listing settings", {
            "fields": ("is_24x7", "is_active"),
            "description": "24x7 describes opening hours, not current beds or service availability. Active controls whether a record is eligible for later public listings.",
        }),
        ("Record information", {
            "fields": ("demo_status", "demo_key", "created_at", "updated_at"),
            "description": "FAKE sample locations and phone numbers are for learning only. Ordinary entries are not automatically verified.",
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("specialities")

    @admin.display(description="Specialities")
    def speciality_names(self, obj):
        return ", ".join(speciality.name for speciality in obj.specialities.all()) or "—"

    @admin.display(boolean=True, description="FAKE sample data")
    def demo_status(self, obj):
        return obj.is_demo
```

### facilities/sample_data.py

Explicitly fictional source records and a helper that converts their defaults to model values.

```python
"""Entirely fictional facilities. These are not healthcare recommendations."""

from decimal import Decimal

from .models import Facility

DEMO_SPECIALITIES = {
    "general-medicine": "General medicine",
    "emergency-care": "Emergency care",
    "cardiology": "Cardiology",
    "paediatrics": "Paediatrics",
    "pharmacy-services": "Pharmacy services",
    "blood-services": "Blood services",
}

# Synthetic positions in one cluster for later distance-search practice.
# They are not the positions of actual facilities. Never call the dummy number.
DEMO_FACILITIES = (
    {
        "key": "medtap-demo-hospital-alpha", "name": "FAKE Demo Hospital Alpha",
        "type": Facility.Type.HOSPITAL, "latitude": "12.970000", "longitude": "77.590000",
        "specialities": ("general-medicine", "emergency-care", "cardiology"),
        "is_24x7": True, "is_active": True,
    },
    {
        "key": "medtap-demo-hospital-beta", "name": "FAKE Demo Hospital Beta",
        "type": Facility.Type.HOSPITAL, "latitude": "12.980000", "longitude": "77.600000",
        "specialities": ("general-medicine", "paediatrics"),
        "is_24x7": False, "is_active": True,
    },
    {
        "key": "medtap-demo-clinic-alpha", "name": "FAKE Demo Clinic Alpha",
        "type": Facility.Type.CLINIC, "latitude": "12.975000", "longitude": "77.585000",
        "specialities": ("general-medicine",), "is_24x7": False, "is_active": True,
    },
    {
        "key": "medtap-demo-clinic-beta", "name": "FAKE Demo Clinic Beta",
        "type": Facility.Type.CLINIC, "latitude": "12.960000", "longitude": "77.605000",
        "specialities": ("paediatrics",), "is_24x7": False, "is_active": True,
    },
    {
        "key": "medtap-demo-pharmacy-alpha", "name": "FAKE Demo Pharmacy Alpha",
        "type": Facility.Type.PHARMACY, "latitude": "12.968000", "longitude": "77.595000",
        "specialities": ("pharmacy-services",), "is_24x7": True, "is_active": True,
    },
    {
        "key": "medtap-demo-pharmacy-beta", "name": "FAKE Demo Pharmacy Beta",
        "type": Facility.Type.PHARMACY, "latitude": "12.990000", "longitude": "77.610000",
        "specialities": ("pharmacy-services",), "is_24x7": False, "is_active": False,
    },
    {
        "key": "medtap-demo-blood-bank-alpha", "name": "FAKE Demo Blood Bank Alpha",
        "type": Facility.Type.BLOOD_BANK, "latitude": "12.965000", "longitude": "77.580000",
        "specialities": ("blood-services",), "is_24x7": True, "is_active": True,
    },
    {
        "key": "medtap-demo-blood-bank-beta", "name": "FAKE Demo Blood Bank Beta",
        "type": Facility.Type.BLOOD_BANK, "latitude": "12.985000", "longitude": "77.575000",
        "specialities": ("blood-services",), "is_24x7": False, "is_active": True,
    },
)


def facility_defaults(sample, position):
    return {
        "name": sample["name"],
        "facility_type": sample["type"],
        "address": f"FAKE address {position}, Example Road, Demo District. No real facility exists here.",
        "phone": "0000000000",
        "latitude": Decimal(sample["latitude"]),
        "longitude": Decimal(sample["longitude"]),
        "is_24x7": sample["is_24x7"],
        "is_active": sample["is_active"],
    }
```

### facilities/management/__init__.py

Create an empty package marker.

```python

```

### facilities/management/commands/__init__.py

Create an empty package marker.

```python

```

### facilities/management/commands/seed_demo_facilities.py

Repeatable, validated, atomic creation of missing FAKE samples.

```python
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from facilities.models import Facility, Speciality
from facilities.sample_data import DEMO_FACILITIES, DEMO_SPECIALITIES, facility_defaults


class Command(BaseCommand):
    help = "Add 8 clearly labelled FAKE facilities. Reruns keep existing records and admin edits."
    requires_migrations_checks = True

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0
        speciality_count = 0
        try:
            with transaction.atomic():
                specialities = {}
                for slug, name in DEMO_SPECIALITIES.items():
                    speciality = Speciality.objects.filter(slug=slug).first()
                    if speciality is None:
                        speciality = Speciality.objects.filter(name=name).first()
                    if speciality is None:
                        speciality = Speciality(name=name, slug=slug)
                        speciality.full_clean()
                        speciality.save()
                        speciality_count += 1
                    specialities[slug] = speciality

                for position, sample in enumerate(DEMO_FACILITIES, start=1):
                    # Stable unique keys survive renaming a demo facility in admin.
                    if Facility.objects.filter(demo_key=sample["key"]).exists():
                        skipped_count += 1
                        continue
                    defaults = facility_defaults(sample, position)
                    candidate = Facility(demo_key=sample["key"], **defaults)
                    candidate.full_clean(validate_unique=False)
                    facility, created = Facility.objects.get_or_create(
                        demo_key=sample["key"], defaults=defaults,
                    )
                    if created:
                        facility.specialities.set(specialities[slug] for slug in sample["specialities"])
                        created_count += 1
                    else:
                        skipped_count += 1
        except ValidationError as error:
            raise CommandError("Invalid demo data; no changes saved: " + "; ".join(error.messages)) from error
        except IntegrityError as error:
            raise CommandError("Demo data could not be saved; the transaction was rolled back.") from error

        self.stdout.write(self.style.SUCCESS(
            f"Created {created_count} FAKE facilities; kept {skipped_count} existing demo records. "
            f"Created {speciality_count} specialities."
        ))
        self.stdout.write("Demo phone 0000000000 and all demo addresses/locations are fictional. Do not call or navigate to them.")
```

### facilities/migrations/0002_facility_demo_key.py

Generated schema change. Commit this alongside the model; do not edit an already applied migration.

```python
# Generated by Django 6.1.3 on 2026-11-10 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facilities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='facility',
            name='demo_key',
            field=models.SlugField(blank=True, editable=False, help_text='Stable identifier for generated FAKE sample data; blank for ordinary facilities.', null=True, unique=True),
        ),
    ]
```

### facilities/tests.py

26 facility/model/admin/command tests; together with 34 account tests, the current suite contains 60 tests.

```python
from copy import deepcopy
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User

from .models import Facility, Speciality
from .sample_data import DEMO_FACILITIES, DEMO_SPECIALITIES


def facility_data(**changes):
    data = {
        "name": "FAKE Test Hospital", "facility_type": Facility.Type.HOSPITAL,
        "address": "FAKE test address", "phone": "0000000000",
        "latitude": Decimal("12.970000"), "longitude": Decimal("77.590000"),
        "is_active": True,
    }
    data.update(changes)
    return data


class FacilityModelTests(TestCase):
    def test_valid_facility_with_multiple_specialities(self):
        facility = Facility(**facility_data())
        facility.full_clean()
        facility.save()
        first = Speciality.objects.create(name="Demo One", slug="demo-one")
        second = Speciality.objects.create(name="Demo Two", slug="demo-two")
        facility.specialities.set([first, second])
        self.assertEqual(facility.specialities.count(), 2)
        self.assertEqual(str(facility), facility.name)

    def test_invalid_coordinates_phone_and_type_are_rejected(self):
        for field, value in (
            ("latitude", Decimal("90.000001")), ("latitude", Decimal("-90.000001")),
            ("longitude", Decimal("180.000001")), ("longitude", Decimal("-180.000001")),
            ("phone", "not-a-phone"), ("facility_type", "invalid"),
        ):
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValidationError) as error:
                    Facility(**facility_data(**{field: value})).full_clean()
                self.assertIn(field, error.exception.message_dict)

    def test_coordinate_boundaries_are_valid(self):
        for latitude, longitude in (("90", "180"), ("-90", "-180"), ("0", "0")):
            Facility(**facility_data(latitude=Decimal(latitude), longitude=Decimal(longitude))).full_clean()

    def test_ordinary_facilities_can_have_multiple_null_demo_keys(self):
        first = Facility.objects.create(**facility_data())
        second = Facility.objects.create(**facility_data(name="Another FAKE Test Facility"))
        self.assertIsNone(first.demo_key)
        self.assertIsNone(second.demo_key)
        self.assertFalse(first.is_demo)

    def test_demo_key_is_unique_and_identifies_samples(self):
        first = Facility.objects.create(**facility_data(demo_key="test-demo-key"))
        self.assertTrue(first.is_demo)
        with self.assertRaises(ValidationError) as error:
            Facility(**facility_data(demo_key="test-demo-key")).full_clean()
        self.assertIn("demo_key", error.exception.message_dict)

    def test_deleting_speciality_keeps_facility(self):
        speciality = Speciality.objects.create(name="Demo", slug="demo")
        facility = Facility.objects.create(**facility_data())
        facility.specialities.add(speciality)
        speciality.delete()
        self.assertTrue(Facility.objects.filter(pk=facility.pk).exists())
        self.assertFalse(facility.specialities.exists())


class SeedDemoFacilitiesTests(TestCase):
    def seed(self):
        output = StringIO()
        call_command("seed_demo_facilities", stdout=output)
        return output.getvalue()

    def test_seed_creates_eight_valid_clearly_fake_facilities(self):
        output = self.seed()
        self.assertIn("Created 8 FAKE facilities", output)
        self.assertEqual(Facility.objects.count(), 8)
        self.assertEqual(Speciality.objects.count(), 6)
        for facility in Facility.objects.all():
            facility.full_clean()
            self.assertTrue(facility.name.startswith("FAKE "))
            self.assertIn("FAKE", facility.address)
            self.assertEqual(facility.phone, "0000000000")
            self.assertTrue(facility.is_demo)
            self.assertTrue(facility.specialities.exists())
        for facility_type in Facility.Type.values:
            self.assertEqual(Facility.objects.filter(facility_type=facility_type).count(), 2)
        self.assertTrue(Facility.objects.filter(is_24x7=True).exists())
        self.assertTrue(Facility.objects.filter(is_active=False).exists())

    def test_rerun_does_not_duplicate_rows(self):
        self.seed()
        keys_and_ids = dict(Facility.objects.values_list("demo_key", "pk"))
        output = self.seed()
        self.assertIn("Created 0 FAKE facilities; kept 8", output)
        self.assertEqual(dict(Facility.objects.values_list("demo_key", "pk")), keys_and_ids)
        self.assertEqual(Speciality.objects.count(), len(DEMO_SPECIALITIES))

    def test_rerun_preserves_admin_edits_and_speciality_assignments(self):
        self.seed()
        facility = Facility.objects.get(demo_key=DEMO_FACILITIES[0]["key"])
        facility.name = "FAKE Renamed In Admin"
        facility.address = "FAKE manually edited address"
        facility.is_active = False
        facility.save()
        custom = Speciality.objects.create(name="Custom Demo Speciality", slug="custom-demo")
        facility.specialities.set([custom])
        self.seed()
        facility.refresh_from_db()
        self.assertEqual(facility.name, "FAKE Renamed In Admin")
        self.assertEqual(facility.address, "FAKE manually edited address")
        self.assertFalse(facility.is_active)
        self.assertEqual(list(facility.specialities.all()), [custom])
        self.assertEqual(Facility.objects.count(), 8)

    def test_seed_leaves_existing_ordinary_facility_untouched_even_if_name_matches(self):
        existing = Facility.objects.create(**facility_data(name=DEMO_FACILITIES[0]["name"]))
        self.seed()
        existing.refresh_from_db()
        self.assertIsNone(existing.demo_key)
        self.assertEqual(existing.address, "FAKE test address")
        self.assertEqual(Facility.objects.count(), 9)

    def test_reuses_existing_speciality_by_name_without_changing_slug(self):
        existing = Speciality.objects.create(name="General medicine", slug="existing-general-medicine")
        self.seed()
        existing.refresh_from_db()
        self.assertEqual(existing.slug, "existing-general-medicine")
        self.assertEqual(Speciality.objects.count(), 6)
        self.assertTrue(Facility.objects.get(demo_key=DEMO_FACILITIES[0]["key"]).specialities.filter(pk=existing.pk).exists())

    def test_deleted_demo_facility_is_recreated_without_resetting_other_rows(self):
        self.seed()
        key = DEMO_FACILITIES[0]["key"]
        Facility.objects.get(demo_key=key).delete()
        output = self.seed()
        self.assertIn("Created 1 FAKE facilities; kept 7", output)
        self.assertEqual(Facility.objects.count(), 8)

    def test_invalid_sample_rolls_back_all_facilities_and_specialities(self):
        invalid = deepcopy(list(DEMO_FACILITIES))
        invalid[-1]["latitude"] = "91.000000"
        with patch("facilities.management.commands.seed_demo_facilities.DEMO_FACILITIES", invalid):
            with self.assertRaises(CommandError):
                self.seed()
        self.assertFalse(Facility.objects.exists())
        self.assertFalse(Speciality.objects.exists())


class FacilityAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(username="fake-admin", password=None)
        cls.ordinary_user = User.objects.create_user(username="fake-site-user")
        cls.staff_user = User.objects.create_user(username="fake-limited-staff", is_staff=True)
        cls.speciality = Speciality.objects.create(name="Demo training one", slug="training-one")
        cls.other_speciality = Speciality.objects.create(name="Demo training two", slug="training-two")
        cls.facility = Facility.objects.create(**facility_data())
        cls.facility.specialities.set([cls.speciality, cls.other_speciality])
        cls.demo_facility = Facility.objects.create(**facility_data(
            name="FAKE Demo Clinic", facility_type=Facility.Type.CLINIC,
            demo_key="admin-test-demo", is_active=False,
        ))

    def setUp(self):
        self.client.force_login(self.admin_user)

    def admin_data(self, **changes):
        data = {
            "name": "FAKE Admin Hospital", "facility_type": Facility.Type.HOSPITAL,
            "address": "FAKE admin address", "phone": "0000000000",
            "latitude": "12.970000", "longitude": "77.590000",
            "specialities": [self.speciality.pk], "is_active": "on", "is_24x7": "on",
        }
        data.update(changes)
        return data

    def test_anonymous_and_ordinary_users_cannot_access_facility_admin(self):
        url = reverse("admin:facilities_facility_changelist")
        for user in (None, self.ordinary_user):
            client = Client()
            if user:
                client.force_login(user)
            response = client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse("admin:login"), response.url)

    def test_staff_without_permissions_is_denied(self):
        self.client.force_login(self.staff_user)
        self.assertEqual(self.client.get(reverse("admin:facilities_facility_changelist")).status_code, 403)

    def test_view_only_staff_cannot_add_change_or_delete(self):
        permission = Permission.objects.get(codename="view_facility", content_type__app_label="facilities")
        self.staff_user.user_permissions.add(permission)
        self.client.force_login(self.staff_user)
        self.assertEqual(self.client.get(reverse("admin:facilities_facility_changelist")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:facilities_facility_add")).status_code, 403)
        self.assertEqual(self.client.post(reverse("admin:facilities_facility_change", args=[self.facility.pk]), self.admin_data()).status_code, 403)
        self.assertEqual(self.client.post(reverse("admin:facilities_facility_delete", args=[self.facility.pk]), {"post": "yes"}).status_code, 403)

    def test_admin_lists_and_detail_forms_load(self):
        for url in (
            reverse("admin:facilities_facility_changelist"),
            reverse("admin:facilities_facility_add"),
            reverse("admin:facilities_facility_change", args=[self.facility.pk]),
            reverse("admin:facilities_speciality_changelist"),
            reverse("admin:facilities_speciality_add"),
        ):
            self.assertEqual(self.client.get(url).status_code, 200)

    def test_admin_can_add_facility_and_assign_specialities(self):
        response = self.client.post(reverse("admin:facilities_facility_add"), self.admin_data(demo_key="forged-demo-key"))
        self.assertEqual(response.status_code, 302)
        facility = Facility.objects.get(name="FAKE Admin Hospital")
        self.assertEqual(list(facility.specialities.all()), [self.speciality])
        self.assertTrue(facility.is_24x7)
        self.assertIsNone(facility.demo_key)

    def test_admin_rejects_invalid_coordinates_and_phone(self):
        response = self.client.post(reverse("admin:facilities_facility_add"), self.admin_data(latitude="91", longitude="181", phone="invalid"))
        self.assertEqual(response.status_code, 200)
        errors = response.context["adminform"].form.errors
        for field in ("latitude", "longitude", "phone"):
            self.assertIn(field, errors)
        self.assertFalse(Facility.objects.filter(name="FAKE Admin Hospital").exists())

    def test_admin_can_edit_but_cannot_change_readonly_demo_key(self):
        response = self.client.post(
            reverse("admin:facilities_facility_change", args=[self.demo_facility.pk]),
            self.admin_data(name="FAKE Edited Demo", demo_key="different-key"),
        )
        self.assertEqual(response.status_code, 302)
        self.demo_facility.refresh_from_db()
        self.assertEqual(self.demo_facility.name, "FAKE Edited Demo")
        self.assertEqual(self.demo_facility.demo_key, "admin-test-demo")

    def test_search_by_multiple_specialities_does_not_duplicate_facility(self):
        response = self.client.get(reverse("admin:facilities_facility_changelist"), {"q": "training"})
        self.assertEqual([item.pk for item in response.context["cl"].result_list], [self.facility.pk])

    def test_admin_filters_by_type_active_and_demo_source(self):
        url = reverse("admin:facilities_facility_changelist")
        for filters, expected in (
            ({"facility_type": "hospital"}, self.facility.pk),
            ({"is_active__exact": "0"}, self.demo_facility.pk),
            ({"demo": "yes"}, self.demo_facility.pk),
            ({"demo": "no"}, self.facility.pk),
        ):
            response = self.client.get(url, filters)
            self.assertEqual([item.pk for item in response.context["cl"].result_list], [expected])

    def test_speciality_autocomplete_works_for_admin(self):
        response = self.client.get(reverse("admin:autocomplete"), {
            "app_label": "facilities", "model_name": "facility", "field_name": "specialities", "term": "training",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 2)

    def test_admin_can_add_speciality(self):
        response = self.client.post(reverse("admin:facilities_speciality_add"), {
            "name": "FAKE Test Service", "slug": "fake-test-service",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Speciality.objects.filter(slug="fake-test-service").exists())

    def test_admin_delete_get_confirms_and_post_deletes(self):
        url = reverse("admin:facilities_facility_delete", args=[self.facility.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Facility.objects.filter(pk=self.facility.pk).exists())
        self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 302)
        self.assertFalse(Facility.objects.filter(pk=self.facility.pk).exists())

    def test_admin_writes_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin_user)
        response = client.post(reverse("admin:facilities_facility_add"), self.admin_data())
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Facility.objects.filter(name="FAKE Admin Hospital").exists())
```

## Verification completed

- Django checks pass, the new migration is applied, and migration drift check
  reports No changes detected.
- All 60 facility/account tests pass (26 new facility tests, 34 existing account tests).
- The command seeded eight FAKE facilities and six specialities in the actual
  development database. It did not modify user/profile/contact records.
- Tests exercise admin add/edit/delete, CSRF, anonymous/non-staff/staff/view-only
  access, multiple-speciality search without duplicates, filters and autocomplete.
- Model/seed tests cover all types, coordinate boundaries, invalid values, the
  stable identifier, multiple ordinary NULL keys, repeated runs, existing-name
  collisions, preserved edits, reused specialities, missing-record recreation and
  rollback of invalid batches.
- Live home/admin URLs respond successfully. Unauthenticated facility/speciality
  admin requests correctly redirect to the admin login page. Authenticated admin
  behaviour is checked with Django's test client and isolated test users.

Browser screenshot verification is unavailable in this environment. This step
uses Django's standard admin UI; the authenticated pages were verified through
Django's request/response tests, rather than visual browser automation.

Stop here. Say **next** for Step 4: nearby facility search, distance sorting,
filters, an honest demo-data presentation, and Leaflet/OpenStreetMap.