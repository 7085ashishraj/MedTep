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
