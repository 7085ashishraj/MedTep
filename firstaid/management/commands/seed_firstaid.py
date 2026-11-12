from copy import deepcopy

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from firstaid.content import GUIDES, HELPLINES, SOURCE_CHECKED_ON
from firstaid.models import EmergencyHelpline, FirstAidGuide, FirstAidStep


class Command(BaseCommand):
    help = "Add source-checked educational guides and official helpline references; preserve existing edits."
    requires_migrations_checks = True

    def handle(self, *args, **options):
        guide_count = helpline_count = 0
        try:
            with transaction.atomic():
                for entry in deepcopy(GUIDES):
                    steps = entry.pop("steps")
                    if FirstAidGuide.objects.filter(slug=entry["slug"]).exists():
                        continue
                    guide = FirstAidGuide(**entry, source_checked_on=SOURCE_CHECKED_ON, is_published=True)
                    guide.full_clean()
                    guide.save()
                    for position, (heading, instruction) in enumerate(steps, 1):
                        step = FirstAidStep(guide=guide, position=position, heading=heading, instruction=instruction)
                        step.full_clean()
                        step.save()
                    guide_count += 1
                for entry in deepcopy(HELPLINES):
                    if EmergencyHelpline.objects.filter(number=entry["number"], region=entry["region"]).exists():
                        continue
                    helpline = EmergencyHelpline(**entry, verified_on=SOURCE_CHECKED_ON, is_active=True)
                    helpline.full_clean()
                    helpline.save()
                    helpline_count += 1
        except (ValidationError, IntegrityError) as error:
            raise CommandError(f"Content seed rolled back: {error}") from error
        self.stdout.write(self.style.SUCCESS(
            f"Created {guide_count} guides and {helpline_count} helpline references. Existing records were preserved.\n"
            f"Sources checked on {SOURCE_CHECKED_ON}; clinical review is not recorded. No test calls were made."
        ))
