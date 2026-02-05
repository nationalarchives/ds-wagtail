from uuid import uuid4

from app.api.models import APIToken
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or delete API tokens"

    def add_arguments(self, parser):
        parser.add_argument(
            "identifier", type=str, help="Name for new token, or name/key to delete"
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete the token with the given name or key",
        )
        parser.add_argument(
            "--refresh",
            action="store_true",
            help="Refresh (regenerate) the key for an existing token, or create if doesn't exist",
        )

    def _get_token_by_name_or_key(self, identifier):
        token = APIToken.objects.filter(name=identifier).first()
        if token:
            return token
        return APIToken.objects.filter(key=identifier).first()

    def _delete_token(self, identifier):
        token = self._get_token_by_name_or_key(identifier)
        if not token:
            self.stdout.write(self.style.ERROR(f"Token not found: {identifier}"))
            return

        token_name = token.name
        token_key = token.key
        token.delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted API token: {token_name} ({str(token_key)})"
            )
        )

    def _refresh_token(self, identifier):
        token = APIToken.objects.filter(name=identifier).first()
        if token:
            token.key = uuid4()
            token.save()
            self.stdout.write(
                self.style.SUCCESS(f"Successfully refreshed API token: {identifier}")
            )
        else:
            token = APIToken.objects.create(name=identifier)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created API token: {identifier}")
            )
        self.stdout.write(f"API Key: {str(token.key)}")

    def _create_token(self, identifier):
        existing_token = APIToken.objects.filter(name=identifier).first()
        if existing_token:
            self.stdout.write(self.style.WARNING(f"Token already exists: {identifier}"))
            self.stdout.write(f"API Key: {str(existing_token.key)}")
            return

        token = APIToken.objects.create(name=identifier)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created API token: {identifier}")
        )
        self.stdout.write(f"API Key: {str(token.key)}")

    def handle(self, *args, **options):
        identifier = options["identifier"]
        delete = options["delete"]
        refresh = options["refresh"]

        if delete:
            try:
                self._delete_token(identifier)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to delete API token: {str(e)}")
                )
                raise
        elif refresh:
            try:
                self._refresh_token(identifier)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to refresh API token: {str(e)}")
                )
                raise
        else:
            try:
                self._create_token(identifier)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to create API token: {str(e)}")
                )
                raise
