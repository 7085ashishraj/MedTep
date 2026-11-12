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
