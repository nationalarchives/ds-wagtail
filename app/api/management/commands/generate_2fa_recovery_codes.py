from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils.crypto import get_random_string
from django_otp.plugins.otp_static.models import StaticDevice

User = get_user_model()

# Don't include commonly misunderstood characters
ALLOWED_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


class Command(BaseCommand):
    help = "Regenerate 2FA recovery codes for a user."

    def add_arguments(self, parser):
        parser.add_argument(
            "--target-email",
            required=True,
            help="Email of the user whose recovery codes should be regenerated.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=10,
            help="Number of recovery codes to generate (default: 10).",
        )
        parser.add_argument(
            "--length",
            type=int,
            default=10,
            help="Length of each recovery code (default: 10, max: 16).",
        )
        parser.add_argument(
            "--show-codes",
            action="store_true",
            help="Print generated recovery codes to stdout.",
        )

    def _get_target_user(self, target_email):
        user = User.objects.filter(email__iexact=target_email).first()
        if not user:
            raise CommandError(
                self.style.ERROR(f"No user found with email: {target_email}")
            )

        if not user.is_active:
            raise CommandError(self.style.ERROR("Target user is inactive."))

        return user

    def _validate_inputs(self, count, length):
        if count < 1 or count > 50:
            raise CommandError("--count must be between 1 and 50")

        if length < 6 or length > 16:
            raise CommandError("--length must be between 6 and 16")

    def handle(self, *args, **options):
        target_email = options["target_email"].strip().lower()
        count = options["count"]
        length = options["length"]
        show_codes = options["show_codes"]

        self._validate_inputs(count, length)
        user = self._get_target_user(target_email)

        StaticDevice.objects.filter(user=user).delete()

        device = StaticDevice.objects.create(
            user=user,
            name="Recovery codes",
            confirmed=True,
        )

        codes = [
            get_random_string(length=length, allowed_chars=ALLOWED_CHARS)
            for _ in range(count)
        ]
        for code in codes:
            device.token_set.create(token=code)

        self.stdout.write(
            self.style.SUCCESS(f"Generated {count} recovery code(s) for {user.email}.")
        )
        if show_codes:
            for code in codes:
                self.stdout.write(code)
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Recovery codes are hidden by default use the --show-codes flag to print them."
                )
            )
