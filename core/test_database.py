"""Prove migrated database invariants, independently of ModelForm/full_clean."""
from django.db import IntegrityError, transaction
from django.test import TestCase, tag

from accounts.models import EmergencyContact, MedicalProfile, User
from emergency.models import AmbulanceRequest, AmbulanceStatusEvent, EmergencyRequest
from facilities.models import Facility
from firstaid.models import EmergencyHelpline, FirstAidGuide, FirstAidStep


@tag("database")
class DatabaseInvariantTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username="fake-constraint-owner")
        cls.profile = MedicalProfile.objects.create(user=cls.owner)
        cls.sos = EmergencyRequest.objects.create(user=cls.owner, latitude=0, longitude=0)

    def test_database_allows_only_one_profile_per_user(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MedicalProfile.objects.create(user=self.owner)
        self.assertEqual(MedicalProfile.objects.filter(user=self.owner).count(), 1)

    def test_primary_contact_constraint_is_scoped_to_each_profile(self):
        values = {"name": "FAKE contact", "relationship": "Friend", "phone": "0000000000"}
        EmergencyContact.objects.create(profile=self.profile, is_primary=True, **values)
        with self.assertRaises(IntegrityError), transaction.atomic():
            EmergencyContact.objects.create(profile=self.profile, is_primary=True, **values)
        EmergencyContact.objects.create(profile=self.profile, is_primary=False, **values)
        other = MedicalProfile.objects.create(user=User.objects.create_user(username="fake-other-profile"))
        EmergencyContact.objects.create(profile=other, is_primary=True, **values)
        self.assertEqual(EmergencyContact.objects.filter(is_primary=True).count(), 2)

    def test_database_rejects_out_of_range_facility_coordinates(self):
        for latitude, longitude in (("90.000001", "0"), ("-90.000001", "0"), ("0", "180.000001"), ("0", "-180.000001")):
            with self.subTest(latitude=latitude, longitude=longitude):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Facility.objects.create(
                        name="FAKE invalid coordinate facility", facility_type="hospital", address="FAKE test address",
                        phone="0000000000", latitude=latitude, longitude=longitude,
                    )
        self.assertFalse(Facility.objects.exists())

    def test_database_rejects_out_of_range_sos_coordinates(self):
        for latitude, longitude in (("90.000001", "0"), ("-90.000001", "0"), ("0", "180.000001"), ("0", "-180.000001")):
            with self.subTest(latitude=latitude, longitude=longitude):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    EmergencyRequest.objects.create(user=self.owner, latitude=latitude, longitude=longitude)
        self.assertEqual(EmergencyRequest.objects.count(), 1)

    def test_database_allows_only_one_transport_per_sos(self):
        first = AmbulanceRequest.objects.create(emergency=self.sos)
        with self.assertRaises(IntegrityError), transaction.atomic():
            AmbulanceRequest.objects.create(emergency=self.sos)
        self.assertEqual(AmbulanceRequest.objects.get(emergency=self.sos), first)

    def test_database_prevents_duplicate_status_events_without_blocking_next_status(self):
        ambulance = AmbulanceRequest.objects.create(emergency=self.sos)
        AmbulanceStatusEvent.objects.create(ambulance=ambulance, status="requested", changed_by=self.owner)
        with self.assertRaises(IntegrityError), transaction.atomic():
            AmbulanceStatusEvent.objects.create(ambulance=ambulance, status="requested", changed_by=self.owner)
        AmbulanceStatusEvent.objects.create(ambulance=ambulance, status="accepted", changed_by=self.owner)
        self.assertEqual(ambulance.status_events.count(), 2)

    def test_firstaid_positions_are_positive_and_unique_within_each_guide(self):
        guide = FirstAidGuide.objects.create(title="FAKE draft guide", slug="fake-constraint-guide", summary="Test only")
        FirstAidStep.objects.create(guide=guide, position=1, instruction="FAKE fixture; not advice")
        for position in (0, 1):
            with self.subTest(position=position):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    FirstAidStep.objects.create(guide=guide, position=position, instruction="FAKE invalid fixture")
        other = FirstAidGuide.objects.create(title="FAKE second draft", slug="fake-other-guide", summary="Test only")
        FirstAidStep.objects.create(guide=other, position=1, instruction="FAKE fixture; not advice")
        self.assertEqual(FirstAidStep.objects.count(), 2)

    def test_helpline_number_uniqueness_is_scoped_to_region(self):
        EmergencyHelpline.objects.create(name="FAKE draft reference", number="112", region="FAKE region A")
        with self.assertRaises(IntegrityError), transaction.atomic():
            EmergencyHelpline.objects.create(name="FAKE duplicate reference", number="112", region="FAKE region A")
        EmergencyHelpline.objects.create(name="FAKE other reference", number="112", region="FAKE region B")
        self.assertEqual(EmergencyHelpline.objects.count(), 2)

    def test_deleting_account_removes_contacts_but_retains_unowned_emergency_history(self):
        EmergencyContact.objects.create(profile=self.profile, name="FAKE disposable contact", relationship="Friend", phone="0000000000")
        ambulance = AmbulanceRequest.objects.create(emergency=self.sos)
        event = AmbulanceStatusEvent.objects.create(ambulance=ambulance, status="requested", changed_by=self.owner)
        self.owner.delete()
        self.assertFalse(MedicalProfile.objects.exists())
        self.assertFalse(EmergencyContact.objects.exists())
        self.sos.refresh_from_db()
        event.refresh_from_db()
        self.assertIsNone(self.sos.user_id)
        self.assertIsNone(event.changed_by_id)
        self.assertTrue(AmbulanceRequest.objects.filter(pk=ambulance.pk).exists())
