from unittest.mock import patch

from django.contrib.auth import SESSION_KEY
from django.core.exceptions import ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import EmergencyContact, MedicalProfile, User
from .services import save_emergency_contact

# Fictional test credentials/data; the test runner uses a separate test database.
TEST_PASSWORD = "Harbor!River92-Train"


def registration_data(**changes):
    data = {
        "first_name": "Fictional", "last_name": "Student", "username": "new-student",
        "email": "student@example.invalid", "password1": TEST_PASSWORD,
        "password2": TEST_PASSWORD,
    }
    data.update(changes)
    return data


def contact_data(**changes):
    data = {
        "name": "Fictional Contact", "relationship": "Sibling", "phone": "0000000000",
    }
    data.update(changes)
    return data


class RegistrationTests(TestCase):
    def test_public_auth_pages_render_and_are_not_cached(self):
        for name in ("accounts:register", "accounts:login"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "csrfmiddlewaretoken")
            self.assertIn("no-store", response["Cache-Control"])

    def test_registration_creates_profile_hashes_password_and_logs_in(self):
        response = self.client.post(reverse("accounts:register"), registration_data(
            is_staff="on", is_superuser="on",
        ))
        self.assertRedirects(response, reverse("accounts:profile_edit"), fetch_redirect_response=False)
        user = User.objects.get(username="new-student")
        self.assertTrue(user.check_password(TEST_PASSWORD))
        self.assertNotEqual(user.password, TEST_PASSWORD)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(MedicalProfile.objects.get(user=user).blood_group, "unknown")
        self.assertEqual(self.client.session[SESSION_KEY], str(user.pk))

    def test_registered_user_can_sign_out_and_sign_back_in_with_same_credentials(self):
        data = registration_data()
        response = self.client.post(reverse("accounts:register"), data)
        self.assertRedirects(response, reverse("accounts:profile_edit"), fetch_redirect_response=False)
        user = User.objects.get(username=data["username"])
        self.client.post(reverse("accounts:logout"))
        self.assertNotIn(SESSION_KEY, self.client.session)
        response = self.client.post(reverse("accounts:login"), {
            "username": data["username"], "password": data["password1"],
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        self.assertEqual(self.client.session[SESSION_KEY], str(user.pk))

    def test_duplicate_username_is_rejected_without_showing_password(self):
        User.objects.create_user(username="new-student")
        response = self.client.post(reverse("accounts:register"), registration_data())
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.context["form"].errors)
        self.assertNotContains(response, TEST_PASSWORD)
        self.assertEqual(User.objects.count(), 1)

    def test_weak_or_mismatched_passwords_are_rejected(self):
        for changes in (
            {"password1": "12345678", "password2": "12345678"},
            {"password2": "A-different-password-93!"},
        ):
            response = self.client.post(reverse("accounts:register"), registration_data(**changes))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
        self.assertFalse(User.objects.exists())

    def test_registration_summary_explains_failure_and_links_exact_field_errors(self):
        response = self.client.post(reverse("accounts:register"), registration_data(
            password1="12345678", password2="12345678",
        ))
        self.assertContains(response, "Your account hasn't been created")
        self.assertContains(response, 'id="form-error-summary"')
        self.assertContains(response, 'href="#id_password2"')
        self.assertContains(response, "This password is too common.", count=2)
        self.assertFalse(User.objects.exists())

    def test_invalid_email_is_rejected_but_blank_email_is_optional(self):
        response = self.client.post(reverse("accounts:register"), registration_data(email="invalid"))
        self.assertIn("email", response.context["form"].errors)
        response = self.client.post(reverse("accounts:register"), registration_data(email=""))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.get(username="new-student").email, "")

    def test_profile_creation_failure_rolls_back_user_creation(self):
        with patch("accounts.views.MedicalProfile.objects.create", side_effect=RuntimeError("Test failure")):
            with self.assertRaises(RuntimeError):
                self.client.post(reverse("accounts:register"), registration_data())
        self.assertFalse(User.objects.exists())
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_csrf_is_required_and_valid_token_allows_registration(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("accounts:register"), registration_data())
        self.assertEqual(response.status_code, 403)
        client.get(reverse("accounts:register"))
        token = client.cookies["csrftoken"].value
        response = client.post(reverse("accounts:register"), registration_data(csrfmiddlewaretoken=token))
        self.assertEqual(response.status_code, 302)
        self.assertIn(SESSION_KEY, client.session)


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="fictional-student", password=TEST_PASSWORD)

    def credentials(self, **extra):
        return {"username": self.user.username, "password": TEST_PASSWORD, **extra}

    def test_login_redirects_to_profile(self):
        response = self.client.post(reverse("accounts:login"), self.credentials())
        self.assertRedirects(response, reverse("accounts:profile"), fetch_redirect_response=False)
        self.assertEqual(self.client.session[SESSION_KEY], str(self.user.pk))

    def test_invalid_credentials_do_not_log_in_or_echo_password(self):
        response = self.client.post(reverse("accounts:login"), self.credentials(password="wrong-password"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertNotContains(response, "wrong-password")

    def test_inactive_user_cannot_log_in(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        response = self.client.post(reverse("accounts:login"), self.credentials())
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_safe_local_next_is_preserved(self):
        destination = reverse("accounts:profile_edit")
        response = self.client.get(reverse("accounts:login"), {"next": destination})
        self.assertEqual(response.context["next"], destination)
        response = self.client.post(reverse("accounts:login"), self.credentials(next=destination))
        self.assertRedirects(response, destination, fetch_redirect_response=False)

    @override_settings(LOGIN_REDIRECT_URL="/accounts/profile/")
    def test_default_destination_accepts_a_url_path_as_well_as_a_route_name(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["next"], "/accounts/profile/")

    def test_https_login_rejects_an_http_redirect(self):
        response = self.client.post(
            reverse("accounts:login"), self.credentials(next="http://testserver/accounts/profile/edit/"),
            secure=True,
        )
        self.assertRedirects(response, reverse("accounts:profile"), fetch_redirect_response=False)

    def test_external_and_protocol_relative_next_are_rejected(self):
        for destination in ("https://attacker.example/", "//attacker.example/", "///attacker.example/", "javascript:alert(1)"):
            client = Client()
            response = client.post(reverse("accounts:login"), self.credentials(next=destination))
            self.assertRedirects(response, reverse("accounts:profile"), fetch_redirect_response=False)

    def test_logout_is_post_only_and_flushes_session(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        self.assertIn(SESSION_KEY, self.client.session)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("core:home"))
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_logout_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(reverse("accounts:logout")).status_code, 403)
        self.assertIn(SESSION_KEY, client.session)
        client.get(reverse("accounts:profile"))
        token = client.cookies["csrftoken"].value
        response = client.post(reverse("accounts:logout"), {"csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(SESSION_KEY, client.session)

    def test_signed_in_users_are_redirected_away_from_auth_pages(self):
        self.client.force_login(self.user)
        for name in ("accounts:login", "accounts:register"):
            self.assertRedirects(self.client.get(reverse(name)), reverse("accounts:profile"))


class OwnedProfileTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="fictional-owner", first_name="Fictional")
        cls.other = User.objects.create_user(username="other-student")
        cls.profile = MedicalProfile.objects.create(user=cls.user)
        cls.other_profile = MedicalProfile.objects.create(user=cls.other, allergies="OTHER PRIVATE NOTE")
        cls.foreign_contact = EmergencyContact.objects.create(
            profile=cls.other_profile, name="Other Private Contact", relationship="Friend", phone="0000000001",
        )

    def setUp(self):
        self.client.force_login(self.user)


class ProfileTests(OwnedProfileTestCase):
    def test_anonymous_users_must_log_in(self):
        client = Client()
        for name, args in (
            ("accounts:profile", []), ("accounts:profile_edit", []),
            ("accounts:contact_add", []), ("accounts:contact_edit", [self.foreign_contact.pk]),
            ("accounts:contact_delete", [self.foreign_contact.pk]),
        ):
            destination = reverse(name, args=args)
            response = client.get(destination)
            self.assertRedirects(response, reverse("accounts:login") + "?next=" + destination)

    def test_profile_only_displays_owned_data_and_is_not_cached(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertContains(response, "Fictional")
        self.assertNotContains(response, "OTHER PRIVATE NOTE")
        self.assertNotContains(response, "Other Private Contact")
        self.assertIn("no-store", response["Cache-Control"])

    def test_profile_update_ignores_forged_ownership_fields(self):
        response = self.client.post(reverse("accounts:profile_edit"), {
            "blood_group": "AB+", "allergies": "Fictional allergy", "medical_conditions": "Fictional condition",
            "user": self.other.pk, "id": self.other_profile.pk,
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        self.profile.refresh_from_db()
        self.other_profile.refresh_from_db()
        self.assertEqual(self.profile.blood_group, "AB+")
        self.assertEqual(self.profile.user_id, self.user.pk)
        self.assertEqual(self.other_profile.allergies, "OTHER PRIVATE NOTE")

    def test_invalid_blood_group_and_oversized_notes_do_not_save(self):
        response = self.client.post(reverse("accounts:profile_edit"), {
            "blood_group": "Z+", "allergies": "x" * 2001, "medical_conditions": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("blood_group", response.context["form"].errors)
        self.assertIn("allergies", response.context["form"].errors)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.allergies, "")

    def test_medical_text_is_escaped(self):
        self.profile.allergies = '<script>alert("fictional")</script>'
        self.profile.save()
        response = self.client.get(reverse("accounts:profile"))
        self.assertNotContains(response, '<script>alert("fictional")</script>')
        self.assertContains(response, "&lt;script&gt;")

    def test_existing_account_without_profile_gets_one_only_on_save(self):
        self.profile.delete()
        self.assertEqual(self.client.get(reverse("accounts:profile")).status_code, 200)
        self.assertEqual(self.client.get(reverse("accounts:profile_edit")).status_code, 200)
        self.assertFalse(MedicalProfile.objects.filter(user=self.user).exists())
        self.assertRedirects(self.client.get(reverse("accounts:contact_add")), reverse("accounts:profile_edit"))
        response = self.client.post(reverse("accounts:profile_edit"), {
            "blood_group": "unknown", "allergies": "", "medical_conditions": "",
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        self.assertEqual(MedicalProfile.objects.filter(user=self.user).count(), 1)


class ContactTests(OwnedProfileTestCase):
    def test_add_normalises_phone_and_ignores_forged_profile(self):
        response = self.client.post(reverse("accounts:contact_add"), contact_data(
            phone="(00000) 00000", profile=self.other_profile.pk,
        ))
        self.assertRedirects(response, reverse("accounts:profile"))
        contact = self.profile.emergency_contacts.get()
        self.assertEqual(contact.phone, "0000000000")
        self.assertFalse(contact.is_primary)

    def test_invalid_phone_and_blank_name_are_rejected(self):
        response = self.client.post(reverse("accounts:contact_add"), contact_data(name="  ", phone="abc"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("phone", response.context["form"].errors)
        self.assertIn("name", response.context["form"].errors)
        self.assertFalse(self.profile.emergency_contacts.exists())

    def test_new_primary_contact_replaces_old_primary(self):
        old = EmergencyContact.objects.create(profile=self.profile, is_primary=True, **contact_data())
        response = self.client.post(reverse("accounts:contact_add"), contact_data(name="New Fictional Contact", is_primary="on"))
        self.assertRedirects(response, reverse("accounts:profile"))
        old.refresh_from_db()
        self.assertFalse(old.is_primary)
        self.assertEqual(self.profile.emergency_contacts.filter(is_primary=True).get().name, "New Fictional Contact")

    def test_editing_contact_can_switch_primary(self):
        old = EmergencyContact.objects.create(profile=self.profile, is_primary=True, **contact_data())
        target = EmergencyContact.objects.create(profile=self.profile, **contact_data(name="Second Fictional Contact"))
        response = self.client.post(reverse("accounts:contact_edit", args=[target.pk]), contact_data(
            name="Updated Fictional Contact", is_primary="on",
        ))
        self.assertRedirects(response, reverse("accounts:profile"))
        old.refresh_from_db()
        target.refresh_from_db()
        self.assertFalse(old.is_primary)
        self.assertTrue(target.is_primary)
        self.assertEqual(target.name, "Updated Fictional Contact")

    def test_foreign_contacts_cannot_be_read_edited_or_deleted(self):
        for route in ("accounts:contact_edit", "accounts:contact_delete"):
            url = reverse(route, args=[self.foreign_contact.pk])
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, contact_data()).status_code, 404)
        self.foreign_contact.refresh_from_db()
        self.assertEqual(self.foreign_contact.name, "Other Private Contact")

    def test_remove_get_only_confirms_and_post_deletes(self):
        contact = EmergencyContact.objects.create(profile=self.profile, **contact_data())
        url = reverse("accounts:contact_delete", args=[contact.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(EmergencyContact.objects.filter(pk=contact.pk).exists())
        self.assertRedirects(self.client.post(url), reverse("accounts:profile"))
        self.assertFalse(EmergencyContact.objects.filter(pk=contact.pk).exists())

    def test_contact_mutations_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        contact = EmergencyContact.objects.create(profile=self.profile, **contact_data())
        for url in (
            reverse("accounts:contact_add"), reverse("accounts:contact_edit", args=[contact.pk]),
            reverse("accounts:contact_delete", args=[contact.pk]), reverse("accounts:profile_edit"),
        ):
            self.assertEqual(client.post(url, contact_data()).status_code, 403)
        self.assertEqual(self.profile.emergency_contacts.count(), 1)

    def test_failed_save_rolls_back_primary_switch(self):
        old = EmergencyContact.objects.create(profile=self.profile, is_primary=True, **contact_data())
        with self.assertRaises(ValidationError):
            save_emergency_contact(profile=self.profile, data=contact_data(phone="invalid", is_primary=True))
        old.refresh_from_db()
        self.assertTrue(old.is_primary)
        self.assertEqual(self.profile.emergency_contacts.count(), 1)

    def test_service_rejects_a_contact_from_another_profile(self):
        with self.assertRaises(ValueError):
            save_emergency_contact(profile=self.profile, contact=self.foreign_contact, data=contact_data(is_primary=False))
