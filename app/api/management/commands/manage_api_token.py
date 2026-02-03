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

    def handle(self, *args, **options):
        identifier = options["identifier"]
        delete = options["delete"]

        if delete:
            try:
                token = APIToken.objects.filter(name=identifier).first()
                if not token:
                    token = APIToken.objects.filter(key=identifier).first()

                if not token:
                    self.stdout.write(
                        self.style.ERROR(f"Token not found: {identifier}")
                    )
                    return

                token_name = token.name
                token_key = token.key
                token.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully deleted API token: {token_name} ({str(token_key)})"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to delete API token: {str(e)}")
                )
                raise
        else:
            try:
                token = APIToken.objects.create(name=identifier)
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully created API token: {identifier}")
                )
                self.stdout.write(f"API Key: {str(token.key)}")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to create API token: {str(e)}")
                )
                raise
