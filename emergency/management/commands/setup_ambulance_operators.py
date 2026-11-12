from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the operator group with view/change ambulance permissions; assign no users."
    requires_migrations_checks = True

    def handle(self, *args, **options):
        permissions = Permission.objects.filter(
            content_type__app_label="emergency", content_type__model="ambulancerequest",
            codename__in=["view_ambulancerequest", "change_ambulancerequest"],
        )
        if permissions.count() != 2:
            raise CommandError("Run migrate first to create the required model permissions.")
        group, _ = Group.objects.get_or_create(name="Ambulance operators")
        group.permissions.add(*permissions)
        self.stdout.write(self.style.SUCCESS(
            "Operator group is ready. No users were assigned or promoted.\n"
            "In admin, add your chosen user to Ambulance operators and enable Staff status."
        ))
