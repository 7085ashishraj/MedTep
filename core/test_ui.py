from contextlib import nullcontext
from html import unescape
from html.parser import HTMLParser

from django import forms
from django.template.loader import render_to_string
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import MedicalProfile, User


class Markup(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.nodes = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


class SharedUiTests(TestCase):
    def test_public_pages_have_one_main_landmark_named_navigation_and_no_duplicate_ids(self):
        for name in ("core:home", "accounts:login", "accounts:register", "facilities:nearby", "firstaid:guide_list", "firstaid:helplines"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            markup = Markup(response.content.decode())
            self.assertEqual(sum(tag == "main" for tag, _ in markup.nodes), 1)
            self.assertTrue(any(tag == "nav" and a.get("aria-label") == "Main navigation" for tag, a in markup.nodes))
            ids = [a["id"] for _, a in markup.nodes if "id" in a]
            self.assertEqual(len(ids), len(set(ids)), name)
            self.assertNotContains(response, 'id="feature-preview"')

    def test_password_controls_are_optional_buttons_with_existing_input_targets(self):
        for name, count in (("accounts:login", 1), ("accounts:register", 2)):
            response = self.client.get(reverse(name))
            nodes = Markup(response.content.decode()).nodes
            passwords = {a["id"] for tag, a in nodes if tag == "input" and a.get("type") == "password"}
            buttons = [a for tag, a in nodes if tag == "button" and "data-toggle-password" in a]
            self.assertEqual(len(buttons), count)
            for button in buttons:
                self.assertEqual(button["type"], "button")
                self.assertIn(button["aria-controls"], passwords)
                self.assertIn("hidden", button)

    def test_invalid_registration_errors_reference_real_fields_and_descriptions(self):
        response = self.client.post(reverse("accounts:register"), {"username": "", "first_name": ""})
        nodes = Markup(response.content.decode()).nodes
        ids = {a["id"] for _, a in nodes if "id" in a}
        fields = [a for tag, a in nodes if tag == "input" and a.get("aria-invalid") == "true"]
        self.assertTrue(fields)
        for field in fields:
            described = field.get("aria-describedby", "").split()
            self.assertTrue(described)
            self.assertTrue(set(described).issubset(ids), field)
            self.assertTrue(any(tag == "a" and a.get("href") == "#" + field["id"] for tag, a in nodes))
        self.assertIn("Your account hasn't been created", unescape(response.content.decode()))

    def test_hidden_field_errors_do_not_link_to_unfocusable_inputs(self):
        class DemoForm(forms.Form):
            token = forms.IntegerField(widget=forms.HiddenInput)
        form = DemoForm({"token": "bad"})
        self.assertFalse(form.is_valid())
        html = render_to_string("partials/form_errors.html", {"form": form})
        self.assertIn("Reload this page", html)
        self.assertNotIn('href="#id_token"', html)
        self.assertNotIn("Token:", html)

    def test_home_service_cards_all_navigate_to_implemented_pages(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(len(response.context["quick_actions"]), 6)
        self.assertTrue(all(card.get("href") and card.get("status") for card in response.context["quick_actions"]))
        self.assertNotContains(response, "data-bs-toggle=\"modal\"")

    def test_transport_navigation_marks_current_page(self):
        user = User.objects.create_user(username="fake-ui-user")
        self.client.force_login(user)
        response = self.client.get(reverse("emergency:ambulance_start"))
        self.assertTrue(any(tag == "a" and a.get("href") == reverse("emergency:ambulance_start")
                            and a.get("aria-current") == "page" for tag, a in Markup(response.content.decode()).nodes))

    def test_profile_large_unbroken_content_stays_escaped(self):
        user = User.objects.create_user(username="fake-ui-profile")
        MedicalProfile.objects.create(user=user, allergies="<script>" + "A" * 300 + "</script>")
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertNotContains(response, "<script>AAA")
        self.assertContains(response, "&lt;script&gt;AAA")


@override_settings(DEBUG=False, ROOT_URLCONF="core.error_test_urls", ALLOWED_HOSTS=["testserver"])
class ErrorPageTests(TestCase):
    def test_error_pages_keep_their_status_and_hide_diagnostics(self):
        client = Client(raise_request_exception=False)
        for code in (400, 403, 404, 500):
            logger = "django.security.SuspiciousOperation" if code == 400 else "django.request"
            captured_log = self.assertLogs(logger, level="WARNING") if code != 404 else nullcontext()
            with self.subTest(code=code), captured_log:
                response = client.get(f"/_ui-test-error/{code}/")
                self.assertEqual(response.status_code, code)
                self.assertContains(response, 'href="tel:112"', status_code=code)
                self.assertContains(response, 'id="main-content"', status_code=code)
                self.assertNotContains(response, "PRIVATE diagnostic text", status_code=code)

    def test_plain_unknown_url_uses_branded_404(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertContains(response, "Let's find", status_code=404)
