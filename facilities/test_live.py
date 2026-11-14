from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import uuid

from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from . import live
from .forms import FacilitySearchForm
from .models import Facility
from .services import search_facilities


def element(identifier=101, **tags):
    return {"type": "node", "id": identifier, "lat": 0, "lon": 0,
            "tags": {"amenity": "hospital", "name": "FAKE provider fixture", **tags}}


def snapshot(elements=None):
    return {"elements": elements if elements is not None else [element()],
            "retrieved_at": "2026-11-14T10:00:00+00:00", "truncated": False}


class LiveParsingTests(SimpleTestCase):
    def test_all_four_categories_and_way_centres(self):
        for tags, expected in (({"amenity": "hospital"}, "hospital"), ({"amenity": "pharmacy"}, "pharmacy"),
                               ({"healthcare": "clinic"}, "clinic"), ({"healthcare": "blood_donation"}, "blood_bank")):
            item = {"type": "way", "id": 2, "center": {"lat": 0, "lon": 0}, "tags": {"name": "FAKE fixture", **tags}}
            parsed = live.parse_facility(item)
            self.assertEqual(parsed.facility_type, expected)
            self.assertEqual(parsed.pk, "osm-way-2")
            self.assertEqual(parsed.source_url, "https://www.openstreetmap.org/way/2")

    def test_unknown_details_are_not_invented_or_labelled_open_now(self):
        result = live.parse_facility(element())
        self.assertEqual(result.phone, "")
        self.assertEqual(result.opening_hours, "")
        self.assertFalse(result.is_24x7)
        self.assertIn("not provided", result.address)
        self.assertEqual(result.specialities.all(), [])

    def test_phone_hours_address_and_specialities_are_normalised(self):
        result = live.parse_facility(element(**{
            "phone": "(000) 000-0001;bad", "opening_hours": "24/7",
            "addr:housenumber": "3", "addr:street": "FAKE Road", "addr:city": "FAKE City",
            "healthcare:speciality": "cardiology;general",
        }))
        self.assertEqual(result.phone, "0000000001")  # Fictional format-only number; never dialled.
        self.assertTrue(result.is_24x7)
        self.assertEqual(result.address, "3 FAKE Road, FAKE City")
        self.assertEqual([entry.name for entry in result.specialities.all()], ["Cardiology", "General"])
        for value in ("0000000000", "javascript:alert(1)", "112?body=bad", None):
            self.assertEqual(live.normalise_phone(value), "")

    def test_invalid_private_and_non_healthcare_elements_are_ignored(self):
        fixtures = [None, [], {}, element(access="private"), element(disused="yes"), element(amenity="cafe"),
                    {**element(), "lat": "NaN"}, {**element(), "lon": 181}, {**element(), "id": "bad"},
                    {**element(), "type": "way", "center": None}]
        for item in fixtures:
            with self.subTest(item=item):
                self.assertIsNone(live.parse_facility(item))

    def test_request_is_bounded_identified_and_uses_only_numeric_area_data(self):
        with patch("facilities.live.urlopen", return_value=BytesIO(json.dumps(snapshot()).encode())) as opened:
            data = live.request_elements(12.97, 77.59, 5)
        request = opened.call_args.args[0]
        query = parse_qs(urlsplit(request.full_url).query)["data"][0]
        self.assertIn("around:5800,12.97,77.59", query)
        self.assertIn("timeout:12", query)
        self.assertIn("out center tags 2000", query)
        self.assertIn("MEDTAP", request.get_header("User-agent"))
        self.assertEqual(opened.call_args.kwargs["timeout"], 30)
        self.assertEqual(len(data["elements"]), 1)

    def test_incomplete_invalid_and_oversize_provider_responses_are_errors(self):
        for raw in (b"invalid", b'[]', b'{"elements": [], "remark": "timed out"}', b"x" * (live.MAX_BYTES + 1)):
            with patch("facilities.live.urlopen", return_value=BytesIO(raw)):
                with self.assertRaises(live.ProviderUnavailable):
                    live.request_elements(0, 0, 5)

    @override_settings(FACILITIES_OVERPASS_METHOD="POST")
    def test_managed_provider_can_use_post_without_changing_search_code(self):
        with patch("facilities.live.urlopen", return_value=BytesIO(json.dumps(snapshot()).encode())) as opened:
            live.request_elements(0, 0, 5)
        request = opened.call_args.args[0]
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(urlsplit(request.full_url).query, "")
        self.assertIn("around:5800,0.00,0.00", parse_qs(request.data.decode())["data"][0])

    @override_settings(FACILITIES_OVERPASS_URL="http://127.0.0.1/private")
    def test_invalid_provider_configuration_never_makes_a_request(self):
        with patch("facilities.live.urlopen") as opened:
            with self.assertRaises(live.ProviderUnavailable):
                live.request_elements(0, 0, 5)
        opened.assert_not_called()


class LiveCacheTests(SimpleTestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.settings_override = override_settings(
            FACILITIES_LOCK_DIR=Path(self.directory.name) / "provider.lock",
            CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
                    "facilities": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": str(uuid.uuid4())}},
        )
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

    def test_nearby_requests_share_a_rounded_area_cache(self):
        with patch("facilities.live.request_elements", return_value=snapshot()) as request:
            first = live.nearby_listings(12.970001, 77.590001, 5)
            second = live.nearby_listings(12.970002, 77.590002, 5)
        self.assertEqual(first[1], "fresh")
        self.assertEqual(second[1], "cached")
        self.assertEqual(first[0]["retrieved_at"], second[0]["retrieved_at"])
        request.assert_called_once_with(12.97, 77.59, 5)

    def test_outage_uses_only_explicitly_labelled_older_cache_and_cools_down(self):
        with patch("facilities.live.FRESH_SECONDS", 0), patch("facilities.live.request_elements", return_value=snapshot()):
            original = live.nearby_listings(0, 0, 5)
        with patch("facilities.live.request_elements", side_effect=live.ProviderUnavailable("Unavailable")) as request:
            stale = live.nearby_listings(0, 0, 5)
            again = live.nearby_listings(0, 0, 5)
        self.assertEqual(stale[1], "stale")
        self.assertEqual(stale[0]["retrieved_at"], original[0]["retrieved_at"])
        self.assertEqual(again[1], "stale")
        self.assertEqual(request.call_count, 1)

    def test_in_flight_guard_prevents_parallel_provider_calls(self):
        lock = Path(self.directory.name) / "provider.lock"
        lock.mkdir()
        with patch("facilities.live.request_elements") as request:
            result = live.nearby_listings(0, 0, 5)
        self.assertEqual(result[1], "unavailable")
        request.assert_not_called()


@override_settings(FACILITIES_LIVE_ENABLED=True)
class LiveSearchTests(TestCase):
    def setUp(self):
        self.provider = patch("facilities.services.nearby_listings", return_value=(snapshot(), "fresh", ""))
        self.request = self.provider.start()
        self.addCleanup(self.provider.stop)

    def search(self, **params):
        form = FacilitySearchForm({"latitude": 0, "longitude": 0, **params})
        self.assertTrue(form.is_valid(), form.errors)
        return search_facilities(form.cleaned_data)

    def test_normal_search_hides_seeded_fakes_and_returns_provider_records(self):
        Facility.objects.create(name="FAKE seeded hospital", facility_type="hospital", address="FAKE address",
                                phone="0000000000", latitude=0, longitude=0, demo_key="hidden-seed")
        page = self.search()
        self.assertEqual([match.facility.pk for match in page], ["osm-node-101"])
        self.assertEqual(page[0].distance_km, 0)
        self.assertEqual(page.search_metadata["radius_km"], 5)
        self.assertIsNone(page[0].call_url)
        self.assertIn("destination=0.0%2C0.0", page[0].directions_url)

    def test_all_four_category_filters_match_live_tags(self):
        self.request.return_value = (snapshot([
            element(), element(102, amenity="pharmacy"), element(103, amenity="clinic"),
            element(104, healthcare="blood_bank"),
        ]), "fresh", "")
        for category in Facility.Type.values:
            with self.subTest(category=category):
                page = self.search(facility_type=category)
                self.assertEqual(len(page), 1)
                self.assertEqual(page[0].facility.facility_type, category)

    def test_name_speciality_hours_and_radius_filters_apply_before_pagination(self):
        self.request.return_value = (snapshot([
            element(101, name="FAKE Heart Centre", **{"healthcare:speciality": "cardiology", "opening_hours": "24/7"}),
            {**element(102, name="FAKE Far Centre"), "lon": 1},
            element(103, name="FAKE Other Centre"),
        ]), "fresh", "")
        self.assertEqual(self.search().paginator.count, 2)
        page = self.search(q="Heart", speciality="cardiology", open_24x7="on")
        self.assertEqual([item.facility.pk for item in page], ["osm-node-101"])

    def test_duplicate_named_point_and_building_are_not_repeated(self):
        second = element(102)
        second.update(type="way", center={"lat": 0, "lon": .0001})
        self.request.return_value = (snapshot([element(), element(), second]), "fresh", "")
        self.assertEqual(self.search().paginator.count, 1)

    def test_html_api_share_real_ids_sources_filters_and_no_html_injection(self):
        self.request.return_value = (snapshot([element(name="</script><img onerror=bad>")]), "cached", "")
        params = {"latitude": 0, "longitude": 0}
        html = self.client.get(reverse("facilities:nearby"), params)
        api = self.client.get(reverse("facilities:nearby_api"), params)
        self.assertEqual((html.status_code, api.status_code), (200, 200))
        result = api.json()["results"][0]
        self.assertEqual(result["id"], "osm-node-101")
        self.assertEqual(result["source"], "OpenStreetMap")
        self.assertIsNone(result["phone"])
        self.assertEqual(api.json()["search"]["status"], "cached")
        self.assertNotContains(html, "<img onerror=bad>")
        self.assertContains(html, "&lt;/script&gt;")
        self.assertContains(html, 'id="facility-osm-node-101"')

    def test_no_location_never_calls_provider_or_claims_live_results(self):
        response = self.client.get(reverse("facilities:nearby"))
        self.request.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Where would you like to search?")
        self.assertNotContains(response, "Try demo location")

    def test_upstream_failure_is_503_instead_of_a_successful_empty_directory(self):
        self.request.return_value = (None, "unavailable", "Directory unavailable")
        for route in ("facilities:nearby", "facilities:nearby_api"):
            response = self.client.get(reverse(route), {"latitude": 0, "longitude": 0})
            self.assertEqual(response.status_code, 503)
            self.assertIn("no-store", response["Cache-Control"])

    def test_live_radius_is_bounded_and_unknown_specialities_rejected(self):
        for params in ({"radius_km": 26}, {"speciality": "unknown"}):
            response = self.client.get(reverse("facilities:nearby_api"), {"latitude": 0, "longitude": 0, **params})
            self.assertEqual(response.status_code, 400)
        self.request.assert_not_called()
