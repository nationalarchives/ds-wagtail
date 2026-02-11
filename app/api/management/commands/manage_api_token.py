from app.api.models import APIToken
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or delete API tokens"

    def add_arguments(self, parser):
        parser.add_argument("identifier", type=str, help="Name of the token")
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete the token with the given name",
        )
        parser.add_argument(
            "--refresh",
            action="store_true",
            help="Refresh (regenerate) the key for an existing token",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Don't print human-readable output, just the token key (for create/refresh)",
        )

    def _create_token(self, identifier, quiet=False):
        existing_token = APIToken.objects.filter(name=identifier).first()
        if existing_token:
            raise CommandError(
                f"API token already exists for {identifier}, use --refresh to regenerate"
            )

        token = APIToken.objects.create(name=identifier)
        if not quiet:
            self.stdout.write(self.style.SUCCESS(f"Created API token for {identifier}"))
        self.stdout.write(str(token.key))

    def _refresh_token(self, identifier, quiet=False):
        token = APIToken.objects.filter(name=identifier).first()
        if token:
            token.key = token.generate_key()
            token.save()
            if not quiet:
                self.stdout.write(
                    self.style.SUCCESS(f"Refreshed API token for {identifier}")
                )
        else:
            token = APIToken.objects.create(name=identifier)
            if not quiet:
                self.stdout.write(
                    self.style.SUCCESS(f"Created API token for {identifier}")
                )
        self.stdout.write(str(token.key))

    def _delete_token(self, identifier, quiet=False):
        token = APIToken.objects.filter(name=identifier).first()
        if not token:
            raise CommandError(f"No API token found for {identifier}")
        token.delete()
        if not quiet:
            self.stdout.write(self.style.SUCCESS(f"Deleted API token for {identifier}"))

    def handle(self, *args, **options):
        identifier = options["identifier"]
        delete = options["delete"]
        refresh = options["refresh"]
        quiet = options["quiet"]

        if not identifier:
            raise CommandError("Identifier (token name) is required")

        if delete:
            self._delete_token(identifier, quiet)
        elif refresh:
            self._refresh_token(identifier, quiet)
        else:
            self._create_token(identifier, quiet)
