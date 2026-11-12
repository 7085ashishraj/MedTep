from copy import deepcopy
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User

from .content import GUIDES, HELPLINES, SOURCE_CHECKED_ON
from .models import EmergencyHelpline, FirstAidGuide, FirstAidStep
from .services import public_guides, public_helplines, source_link


def guide_values(**changes):
    values = dict(title="Test educational guide", slug="test-guide", summary="Test summary",
                  source_url="https://www.nhs.uk/conditions/burns-and-scalds/",
                  source_checked_on=timezone.localdate(), is_published=True)
    values.update(changes)
    return values


class FirstAidModelTests(TestCase):
    def test_models_default_to_draft_inactive_and_no_clinical_review(self):
        guide = FirstAidGuide(title="Draft", slug="draft", summary="Draft text")
        guide.full_clean()
        self.assertFalse(guide.is_published)
        self.assertIsNone(guide.reviewed_on)
        self.assertIsNone(guide.source_checked_on)
        line = EmergencyHelpline(name="Test", number="112", region="Test region")
        line.full_clean()
        self.assertFalse(line.is_active)
        self.assertFalse(line.is_nationwide)

    def test_published_guide_and_active_helpline_require_source_metadata(self):
        with self.assertRaises(ValidationError):
            FirstAidGuide(**guide_values(source_url="", source_checked_on=None)).full_clean()
        with self.assertRaises(ValidationError):
            EmergencyHelpline(name="Test", number="112", region="Test", is_active=True).full_clean()

    def test_source_urls_reject_non_https_credentials_and_script_schemes(self):
        for url in ("http://example.com/", "javascript:alert(1)", "https://user:pass@example.com/"):
            with self.subTest(url=url):
                with self.assertRaises(ValidationError):
                    FirstAidGuide(**guide_values(source_url=url)).full_clean()
                self.assertIsNone(source_link(url))

    def test_future_check_and_clinical_review_dates_are_rejected(self):
        tomorrow = timezone.localdate() + timedelta(days=1)
        for field in ("source_checked_on", "reviewed_on"):
            with self.assertRaises(ValidationError):
                FirstAidGuide(**guide_values(**{field: tomorrow})).full_clean()
        with self.assertRaises(ValidationError):
            EmergencyHelpline(name="Test", number="112", region="Test", verified_on=tomorrow).full_clean()

    def test_step_order_positive_positions_and_unique_position(self):
        guide = FirstAidGuide.objects.create(**guide_values())
        FirstAidStep.objects.create(guide=guide, position=2, instruction="Second")
        FirstAidStep.objects.create(guide=guide, position=1, instruction="First")
        self.assertEqual(list(guide.steps.values_list("position", flat=True)), [1, 2])
        for position in (0, 1):
            with self.assertRaises(ValidationError):
                FirstAidStep(guide=guide, position=position, instruction="Invalid").full_clean()

    def test_helpline_number_validation_and_region_unique_key(self):
        EmergencyHelpline.objects.create(name="Test", number="112", region="Test region")
        with self.assertRaises(ValidationError):
            EmergencyHelpline(name="Duplicate", number="112", region="Test region").full_clean()
        for number in ("1", "tel:112", "112?body=test", "<script>"):
            with self.assertRaises(ValidationError):
                EmergencyHelpline(name="Test", number=number, region="Other region").full_clean()


class SeedFirstAidTests(TestCase):
    def seed(self):
        output = StringIO()
        call_command("seed_firstaid", stdout=output)
        return output.getvalue()

    def test_seed_creates_five_sourced_adult_guides_and_three_real_helpline_references(self):
        self.assertIn("Created 5 guides and 3 helpline references", self.seed())
        self.assertEqual(FirstAidGuide.objects.count(), 5)
        self.assertEqual(EmergencyHelpline.objects.count(), 3)
        for guide in FirstAidGuide.objects.all():
            guide.full_clean()
            self.assertIsNone(guide.reviewed_on)
            self.assertEqual(guide.source_checked_on, SOURCE_CHECKED_ON)
            self.assertIn("18", guide.audience)
            self.assertEqual(list(guide.steps.values_list("position", flat=True)), list(range(1, guide.steps.count() + 1)))
        for line in EmergencyHelpline.objects.all():
            line.full_clean()
            self.assertEqual(line.verified_on, SOURCE_CHECKED_ON)
        self.assertTrue(EmergencyHelpline.objects.get(number="112").is_nationwide)
        self.assertFalse(EmergencyHelpline.objects.get(number="108").is_nationwide)
        self.assertFalse(EmergencyHelpline.objects.get(number="102").is_nationwide)

    def test_reseed_preserves_edited_or_unpublished_records_and_steps(self):
        self.seed()
        guide = FirstAidGuide.objects.get(slug="adult-cpr")
        guide.summary = "Staff edited summary"
        guide.is_published = False
        guide.source_checked_on = SOURCE_CHECKED_ON - timedelta(days=1)
        guide.save()
        step = guide.steps.first()
        step.instruction = "Staff edited step"
        step.save()
        line = EmergencyHelpline.objects.get(number="108")
        line.is_active = False
        line.description = "Staff edited coverage"
        line.save()
        self.assertIn("Created 0 guides and 0 helpline references", self.seed())
        guide.refresh_from_db(); step.refresh_from_db(); line.refresh_from_db()
        self.assertEqual(guide.summary, "Staff edited summary")
        self.assertFalse(guide.is_published)
        self.assertEqual(guide.source_checked_on, SOURCE_CHECKED_ON - timedelta(days=1))
        self.assertEqual(step.instruction, "Staff edited step")
        self.assertFalse(line.is_active)
        self.assertEqual(line.description, "Staff edited coverage")

    def test_seed_failure_rolls_back_the_whole_new_content_batch(self):
        invalid = deepcopy(GUIDES)
        invalid[-1]["source_url"] = "http://example.com/"
        with patch("firstaid.management.commands.seed_firstaid.GUIDES", invalid):
            with self.assertRaises(CommandError):
                self.seed()
        self.assertEqual(FirstAidGuide.objects.count(), 0)
        self.assertEqual(FirstAidStep.objects.count(), 0)
        self.assertEqual(EmergencyHelpline.objects.count(), 0)

    def test_existing_slug_collision_is_preserved_without_inserting_new_steps(self):
        guide = FirstAidGuide.objects.create(**guide_values(slug=GUIDES[0]["slug"], is_published=False))
        self.seed()
        guide.refresh_from_db()
        self.assertFalse(guide.is_published)
        self.assertFalse(guide.steps.exists())

    def test_content_keeps_key_scope_and_emergency_exceptions(self):
        self.seed()
        cpr = FirstAidGuide.objects.get(slug="adult-cpr")
        self.assertIn("Gasping is not normal breathing", cpr.summary)
        self.assertIn("100–120", " ".join(cpr.steps.values_list("instruction", flat=True)))
        choking = FirstAidGuide.objects.get(slug="adult-choking")
        self.assertIn("Do not use abdominal thrusts in pregnancy", choking.warnings)
        burns = FirstAidGuide.objects.get(slug="thermal-burns")
        self.assertIn("20 minutes", " ".join(burns.steps.values_list("instruction", flat=True)))
        self.assertIn("put it on the face", burns.steps.last().instruction)
        self.assertIn("Patient transport", EmergencyHelpline.objects.get(number="102").name)


class PublicFirstAidTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_firstaid", stdout=StringIO())

    def test_public_library_detail_and_helplines_do_not_require_login(self):
        for name, args in (("guide_list", []), ("guide_detail", ["adult-cpr"]), ("helplines", [])):
            response = self.client.get(reverse(f"firstaid:{name}", args=args))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "This app does not replace calling 112")

    def test_guide_has_numbered_readable_steps_sources_and_honest_review_metadata(self):
        response = self.client.get(reverse("firstaid:guide_detail", args=["adult-cpr"]))
        self.assertContains(response, "Clinical review of this summary is not recorded")
        self.assertContains(response, "Adults (18 years and over)")
        self.assertContains(response, 'class="firstaid-step-number"', count=5)
        self.assertContains(response, "Resuscitation Council UK")
        self.assertContains(response, 'href="tel:112"')
        self.assertNotContains(response, 'href="tel:999"')

    def test_draft_undated_future_empty_and_unsafe_source_guides_are_not_public(self):
        tomorrow = timezone.localdate() + timedelta(days=1)
        for index, changes in enumerate(({"is_published": False}, {"source_checked_on": None},
                                        {"source_checked_on": tomorrow}, {"source_url": "javascript:alert(1)"}, {})):
            guide = FirstAidGuide.objects.create(**guide_values(slug=f"hidden-{index}", **changes))
            if index != 4:
                FirstAidStep.objects.create(guide=guide, position=1, instruction="Hidden instruction")
            self.assertNotIn(guide, public_guides())
            for name in ("guide_detail", "guide_detail_api"):
                self.assertEqual(self.client.get(reverse(f"firstaid:{name}", args=[guide.slug])).status_code, 404)

    def test_unknown_guide_is_404_for_html_and_json(self):
        for name in ("guide_detail", "guide_detail_api"):
            self.assertEqual(self.client.get(reverse(f"firstaid:{name}", args=["missing"])).status_code, 404)

    def test_search_validation_empty_state_and_api_consistency(self):
        html = self.client.get(reverse("firstaid:guide_list"), {"q": "  CPR  "})
        api = self.client.get(reverse("firstaid:guide_list_api"), {"q": "  CPR  "})
        self.assertEqual([g.slug for g in html.context["page_obj"]], [g["slug"] for g in api.json()["results"]])
        self.assertEqual(api.json()["count"], 1)
        self.assertContains(self.client.get(reverse("firstaid:guide_list"), {"q": "no-such-guide"}), "No guides found")
        for name in ("guide_list", "guide_list_api"):
            self.assertEqual(self.client.get(reverse(f"firstaid:{name}"), {"q": "x" * 121}).status_code, 400)
            self.assertEqual(self.client.get(reverse(f"firstaid:{name}"), {"page": "bad"}).status_code, 400)

    def test_pagination_keeps_search_and_limits_response(self):
        for index in range(21):
            guide = FirstAidGuide.objects.create(**guide_values(slug=f"extra-{index}", title=f"Test extra {index:02d}"))
            FirstAidStep.objects.create(guide=guide, position=1, instruction="Test instruction")
        response = self.client.get(reverse("firstaid:guide_list"), {"q": "Test extra"})
        self.assertEqual(len(response.context["cards"]), 20)
        self.assertIn("q=Test+extra", response.context["next_query"])
        api = self.client.get(reverse("firstaid:guide_list_api"), {"q": "Test extra", "page": 2}).json()
        self.assertEqual(len(api["results"]), 1)
        self.assertIsNone(api["next"])
        self.assertIn("q=Test+extra", api["previous"])
        self.assertEqual(self.client.get(reverse("firstaid:guide_list"), {"page": 999}).status_code, 404)

    def test_api_details_include_ordered_steps_sources_and_null_clinical_review(self):
        data = self.client.get(reverse("firstaid:guide_detail_api", args=["adult-cpr"])).json()
        self.assertEqual([s["position"] for s in data["steps"]], [1, 2, 3, 4, 5])
        self.assertEqual(len(data["sources"]), 2)
        self.assertEqual(data["source_checked_on"], SOURCE_CHECKED_ON.isoformat())
        self.assertIsNone(data["clinical_reviewed_on"])

    def test_all_public_pages_and_apis_reject_post(self):
        for name, args in (("guide_list", []), ("guide_detail", ["adult-cpr"]), ("helplines", []),
                           ("guide_list_api", []), ("guide_detail_api", ["adult-cpr"]), ("helplines_api", [])):
            self.assertEqual(self.client.post(reverse(f"firstaid:{name}", args=args)).status_code, 405)

    def test_helplines_have_direct_calls_and_explicit_coverage(self):
        response = self.client.get(reverse("firstaid:helplines"))
        for number in ("112", "108", "102"):
            self.assertContains(response, f'href="tel:{number}"')
        self.assertContains(response, "State/UT dependent", count=2)
        self.assertContains(response, "No test calls were made")
        data = self.client.get(reverse("firstaid:helplines_api")).json()["results"]
        self.assertEqual([row["number"] for row in data], ["112", "108", "102"])
        self.assertTrue(data[0]["is_nationwide"])
        self.assertTrue(all(not row["is_nationwide"] for row in data[1:]))

    def test_inactive_unverified_future_unsafe_or_dummy_helplines_are_hidden(self):
        tomorrow = timezone.localdate() + timedelta(days=1)
        base = dict(name="Hidden line", number="110", region="Test only", is_active=True,
                    source_url="https://www.mha.gov.in/", verified_on=timezone.localdate())
        for index, changes in enumerate(({"is_active": False}, {"verified_on": None}, {"verified_on": tomorrow},
                                        {"source_url": "javascript:alert(1)"}, {"number": "000"}, {"number": "112?body=bad"})):
            line = EmergencyHelpline.objects.create(**(base | {"region": f"Test {index}"} | changes))
            self.assertNotIn(line, public_helplines())
        self.assertEqual(len(self.client.get(reverse("firstaid:helplines_api")).json()["results"]), 3)

    def test_content_is_escaped_and_unsafe_supporting_links_omitted(self):
        guide = FirstAidGuide.objects.get(slug="adult-cpr")
        guide.title = '<img src=x onerror=alert(1)>'
        guide.supporting_source_url = "javascript:alert(1)"
        guide.save()
        response = self.client.get(reverse("firstaid:guide_detail", args=[guide.slug]))
        self.assertContains(response, "&lt;img src=x onerror=alert(1)&gt;")
        self.assertNotContains(response, '<img src=x onerror=alert(1)>')
        self.assertNotContains(response, 'href="javascript:')
        self.assertEqual(len(response.context["sources"]), 1)

    def test_home_navigation_and_footer_use_real_library_pages(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'href="/first-aid/"')
        self.assertContains(response, 'href="/first-aid/helplines/"')
        self.assertNotContains(response, "First-aid guides are not available")


class FirstAidAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(username="fake-content-admin", password=None, email="")
        cls.staff = User.objects.create_user(username="fake-content-staff", is_staff=True)

    def guide_payload(self, **changes):
        values = {
            "title": "Test admin guide", "slug": "test-admin-guide", "summary": "Educational test only",
            "audience": "Adults", "source_url": "https://www.nhs.uk/conditions/burns-and-scalds/",
            "source_checked_on": timezone.localdate().isoformat(), "is_published": "on",
            "steps-TOTAL_FORMS": "1", "steps-INITIAL_FORMS": "0", "steps-MIN_NUM_FORMS": "0", "steps-MAX_NUM_FORMS": "1000",
            "steps-0-position": "1", "steps-0-heading": "Test heading", "steps-0-instruction": "Test instruction",
        }
        values.update(changes)
        return values

    def test_staff_without_permissions_cannot_manage_content(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse("admin:firstaid_firstaidguide_changelist")).status_code, 403)
        self.assertEqual(self.client.get(reverse("admin:firstaid_emergencyhelpline_changelist")).status_code, 403)

    def test_superuser_can_create_published_guide_with_inline_step(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin:firstaid_firstaidguide_add"), self.guide_payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FirstAidGuide.objects.get().steps.get().heading, "Test heading")

    def test_empty_or_gapped_published_steps_are_rejected_in_admin(self):
        self.client.force_login(self.admin)
        url = reverse("admin:firstaid_firstaidguide_add")
        response = self.client.post(url, self.guide_payload(**{"steps-TOTAL_FORMS": "0"}))
        self.assertContains(response, "at least one instruction step")
        response = self.client.post(url, self.guide_payload(**{"steps-0-position": "2"}))
        self.assertContains(response, "consecutively from 1")
        self.assertEqual(FirstAidGuide.objects.count(), 0)

    def test_duplicate_step_positions_are_rejected_in_admin(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin:firstaid_firstaidguide_add"), self.guide_payload(**{
            "steps-TOTAL_FORMS": "2", "steps-1-position": "1", "steps-1-heading": "Duplicate", "steps-1-instruction": "Second",
        }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FirstAidGuide.objects.count(), 0)

    def test_active_helpline_without_verified_source_is_rejected_in_admin(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin:firstaid_emergencyhelpline_add"), {
            "name": "Test invalid line", "number": "112", "region": "Test only", "is_active": "on",
        })
        self.assertContains(response, "official source and its check date")
        self.assertEqual(EmergencyHelpline.objects.count(), 0)
