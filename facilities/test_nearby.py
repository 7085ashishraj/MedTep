from decimal import Decimal
from math import pi

from django.core.paginator import InvalidPage
from django.test import SimpleTestCase, TestCase, override_settings
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


@override_settings(FACILITIES_LIVE_ENABLED=False)
class FacilitySearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.speciality = Speciality.objects.create(name="Demo care", slug="demo-care")
        cls.other_speciality = Speciality.objects.create(name="Demo care two", slug="demo-care-two")
        cls.near = Facility.objects.create(**facility_data(
            name="Z FAKE Near", latitude=0, longitude=0, is_24x7=True,
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
        self.near.demo_key = "test-demo"
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


@override_settings(FACILITIES_LIVE_ENABLED=False)
class NearbyViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.demo = Facility.objects.create(**facility_data(latitude=0, longitude=0))
        cls.hidden = Facility.objects.create(**facility_data(name="Hidden FAKE facility", is_active=False))

    def test_public_html_and_api_are_available_without_login(self):
        response = self.client.get(reverse("facilities:nearby"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.demo.name)
        self.assertNotContains(response, self.hidden.name)
        self.assertNotContains(response, "FAKE sample")
        self.assertContains(response, "This app does not replace calling 112")
        self.assertContains(response, "Call unavailable")
        self.assertContains(response, "Directions to")
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
        for key in ("phone", "call_url", "distance_km"):
            self.assertIsNone(result[key])
        self.assertIs(result["is_demo"], False)
        self.assertTrue(result["directions_url"].startswith("https://www.google.com/maps/dir/"))
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
        self.assertContains(response, "Where would you like to search?")
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
