from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from wagtail.models import Group

User = get_user_model()


def get_excluded_user_ids(filename):
    with open(filename, "r") as f:
        for user_id in f.read().splitlines():
            yield user_id


class Command(BaseCommand):
    """Deactivate beta tester users accounts.

    Excluding:

     - Admin
     - Private Beta Users with @nationalarchives.gov.uk email address
     - Private Beta Users participating in moderated interviews
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "path_to_user_ids_to_exclude_file", help="Path to user file"
        )

    def handle(self, *args, path_to_user_ids_to_exclude_file, **options):
        users_to_deactivate = User.objects.all()

        excluded_user_ids = [
            id for id in get_excluded_user_ids(path_to_user_ids_to_exclude_file)
        ]

        beta_testers_group = Group.objects.get(name="Beta Testers")

        users_to_deactivate = beta_testers_group.user_set.exclude(
            pk__in=excluded_user_ids
        ).exclude(email__endswith="@nationalarchives.gov.uk")

        count = 0
        for user in users_to_deactivate:
            user.is_active = False
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User {user.id} deactivated"))
            count += 1

        self.stdout.write(
            self.style.SUCCESS(f"{count} accounts successfully deactivated")
        )
