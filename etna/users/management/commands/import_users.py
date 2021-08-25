from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from wagtail.core.models import Group

User = get_user_model()


def get_users(filename):
    with open(filename, "r") as f:
        for email in f.read().splitlines():
            first_name, domain = email.split("@")
            last_name = "Beta tester"

            yield first_name, last_name, email


class Command(BaseCommand):
    """Import list of users from text file"""

    def add_arguments(self, parser):
        parser.add_argument("path_to_user_file", help="Path to user file")
        parser.add_argument("password", help="Password for users")

    def handle(self, *args, path_to_user_file, password, **options):

        beta_testers_group = Group.objects.get(name="Beta Testers")

        for first_name, last_name, email in get_users(path_to_user_file):

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User(email=email)
                user.set_password(password)

            user.username = email
            user.first_name = first_name
            user.last_name = last_name

            user.save()

            user.groups.set([beta_testers_group])

            user.save()
