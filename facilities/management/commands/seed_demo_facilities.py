from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from facilities.models import Facility, Speciality
from facilities.sample_data import DEMO_FACILITIES, DEMO_SPECIALITIES, facility_defaults


class Command(BaseCommand):
    help = "Add 8 clearly labelled FAKE facilities. Reruns keep existing records and admin edits."
    requires_migrations_checks = True

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0
        speciality_count = 0
        try:
            with transaction.atomic():
                specialities = {}
                for slug, name in DEMO_SPECIALITIES.items():
                    speciality = Speciality.objects.filter(slug=slug).first()
                    if speciality is None:
                        speciality = Speciality.objects.filter(name=name).first()
                    if speciality is None:
                        speciality = Speciality(name=name, slug=slug)
                        speciality.full_clean()
                        speciality.save()
                        speciality_count += 1
                    specialities[slug] = speciality

                for position, sample in enumerate(DEMO_FACILITIES, start=1):
                    # Stable unique keys survive renaming a demo facility in admin.
                    if Facility.objects.filter(demo_key=sample["key"]).exists():
                        skipped_count += 1
                        continue
                    defaults = facility_defaults(sample, position)
                    candidate = Facility(demo_key=sample["key"], **defaults)
                    candidate.full_clean(validate_unique=False)
                    facility, created = Facility.objects.get_or_create(
                        demo_key=sample["key"], defaults=defaults,
                    )
                    if created:
                        facility.specialities.set(specialities[slug] for slug in sample["specialities"])
                        created_count += 1
                    else:
                        skipped_count += 1
        except ValidationError as error:
            raise CommandError("Invalid demo data; no changes saved: " + "; ".join(error.messages)) from error
        except IntegrityError as error:
            raise CommandError("Demo data could not be saved; the transaction was rolled back.") from error

        self.stdout.write(self.style.SUCCESS(
            f"Created {created_count} FAKE facilities; kept {skipped_count} existing demo records. "
            f"Created {speciality_count} specialities."
        ))
        self.stdout.write("Demo phone 0000000000 and all demo addresses/locations are fictional. Do not call or navigate to them.")
