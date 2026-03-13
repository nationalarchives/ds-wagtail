from app.api.models import APIToken
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Manage API tokens"

    def add_arguments(self, parser):
        parser.add_argument(
            "identifier", type=str, default="", help="Name of the token"
        )
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
        parser.add_argument(
            "--show",
            action="store_true",
            help="Print the token key for the given identifier without modifying it (for existing tokens only)",
        )
        parser.add_argument(
            "--enable",
            action="store_true",
            help="Enable the token with the given identifier (for existing tokens only)",
        )
        parser.add_argument(
            "--disable",
            action="store_true",
            help="Disable the token with the given identifier (for existing tokens only)",
        )

    def _create_token(self, identifier, quiet=False):
        existing_token = APIToken.objects.filter(name=identifier).first()
        if existing_token:
            raise CommandError(
                f"API token already exists for {identifier}, use --show to see it or --refresh to regenerate"
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

    def _show_token(self, identifier, quiet=False):
        token = APIToken.objects.filter(name=identifier).first()
        if token:
            if not quiet:
                self.stdout.write(self.style.SUCCESS(f"API token for {identifier}"))
            self.stdout.write(str(token.key))
        else:
            raise CommandError(f"No API token found for {identifier}")

    def _delete_token(self, identifier, quiet=False):
        token = APIToken.objects.filter(name=identifier).first()
        if not token:
            raise CommandError(f"No API token found for {identifier}")
        token.delete()
        if not quiet:
            self.stdout.write(self.style.SUCCESS(f"Deleted API token for {identifier}"))

    def _enable_token(self, identifier, quiet=False):
        token = APIToken.objects.filter(name=identifier).first()
        if not token:
            raise CommandError(f"No API token found for {identifier}")
        token.active = True
        token.save()
        if not quiet:
            self.stdout.write(self.style.SUCCESS(f"Enabled API token for {identifier}"))

    def _disable_token(self, identifier, quiet=False):
        token = APIToken.objects.filter(name=identifier).first()
        if not token:
            raise CommandError(f"No API token found for {identifier}")
        token.active = False
        token.save()
        if not quiet:
            self.stdout.write(
                self.style.SUCCESS(f"Disabled API token for {identifier}")
            )

    def handle(self, *args, **options):
        identifier = options["identifier"]
        delete = options["delete"]
        refresh = options["refresh"]
        show = options["show"]
        quiet = options["quiet"]
        enable = options["enable"]
        disable = options["disable"]

        if not identifier:
            raise CommandError("Identifier (token name) is required")

        if delete:
            self._delete_token(identifier, quiet)
        elif refresh:
            self._refresh_token(identifier, quiet)
        elif show:
            self._show_token(identifier, quiet)
        elif enable:
            self._enable_token(identifier, quiet)
        elif disable:
            self._disable_token(identifier, quiet)
        else:
            self._create_token(identifier, quiet)
