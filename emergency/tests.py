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
