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
